import time
import win32api
import win32file


def get_mounted_drives() -> dict[str, str]:
    """
    Возвращает {volume_serial: drive_path} для всех подключённых съёмных
    и локальных дисков (кроме системного C:, если не хочешь его сканировать).
    """
    drives = {}
    bitmask = win32api.GetLogicalDrives()
    for i in range(26):
        if not (bitmask >> i) & 1:
            continue
        letter = f"{chr(65 + i)}:\\"
        drive_type = win32file.GetDriveType(letter)
        # DRIVE_REMOVABLE = 2, DRIVE_FIXED = 3 — берём оба, флешка иногда определяется как FIXED
        if drive_type not in (win32file.DRIVE_REMOVABLE, win32file.DRIVE_FIXED):
            continue
        try:
            vol_info = win32api.GetVolumeInformation(letter)
            serial = str(vol_info[1])  # VolumeSerialNumber
            drives[serial] = letter
        except Exception:
            continue  # диск без файловой системы / только вставлен, ещё не готов
    return drives


class UsbWatcher:
    def __init__(self, on_drives_changed, poll_interval=3):
        self.on_drives_changed = on_drives_changed
        self.poll_interval = poll_interval
        self._known = {}
        self._running = False

    def start(self):
        self._running = True
        while self._running:
            current = get_mounted_drives()
            if current.keys() != self._known.keys():
                added = {s: p for s, p in current.items() if s not in self._known}
                removed = set(self._known) - set(current)
                self._known = current
                self.on_drives_changed(current, added, removed)
            time.sleep(self.poll_interval)

    def stop(self):
        self._running = False