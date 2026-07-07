import logging
import os
import threading
from pathlib import Path

import pystray
from PIL import Image, ImageDraw
from win11toast import notify

from app.services.usb_watcher import UsbWatcher
from app.services.recovery_engine import RecoveryEngine, READY_DIR
from app.config import Config

# ============== Логирование в файл ==============
# pythonw не показывает консоль, поэтому print() бесполезен —
# всё важное пишем в файл, иначе при сбое в фоне не поймём, что случилось.

LOG_DIR = Path(os.getenv("LOCALAPPDATA")) / "P2PBackup"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_PATH = LOG_DIR / "daemon.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_PATH, encoding="utf-8"),
    ],
)
logger = logging.getLogger("p2p-backup-daemon")

ready_files: list[tuple[str, str]] = []


def notify_file_ready(basename: str, path: str):
    ready_files.append((basename, path))
    logger.info(f"Файл готов к сохранению: {basename} -> {path}")
    try:
        notify(
            "P2P Backup",
            f"Восстановлен файл: {basename}\nНажмите на иконку в трее, чтобы сохранить.",
        )
    except Exception as ex:
        # Тост может не показаться (например, если центр уведомлений отключён
        # в системе), но это не должно ронять демон.
        logger.warning(f"Не удалось показать уведомление: {ex}")


def log(msg: str):
    logger.info(msg)


def open_ready_files_window(icon=None, item=None):
    from app.ui.ready_files_gui import show_ready_files_window
    show_ready_files_window(ready_files, READY_DIR)


def make_icon_image():
    img = Image.new("RGB", (64, 64), "black")
    d = ImageDraw.Draw(img)
    d.ellipse((8, 8, 56, 56), fill="deepskyblue")
    return img


def run_watcher(engine: RecoveryEngine):
    watcher = UsbWatcher(on_drives_changed=engine.handle_drives_changed, poll_interval=3)
    try:
        watcher.start()
    except Exception:
        logger.exception("Watcher-поток упал с исключением")


def run_daemon():
    logger.info("=== Демон запущен ===")

    try:
        engine = RecoveryEngine(Config.GO_BINARY_PATH, on_file_ready=notify_file_ready)
    except Exception:
        logger.exception("Не удалось инициализировать RecoveryEngine — демон остановлен")
        return

    watcher_thread = threading.Thread(target=run_watcher, args=(engine,), daemon=True)
    watcher_thread.start()

    def quit_app(icon, item):
        logger.info("=== Демон остановлен пользователем ===")
        icon.stop()

    menu = pystray.Menu(
        pystray.MenuItem("Показать восстановленные файлы", open_ready_files_window, default=True),
        pystray.MenuItem("Выход", quit_app)
    )
    icon = pystray.Icon("P2PBackup", make_icon_image(), "P2P Backup Daemon", menu)

    try:
        icon.run()
    except Exception:
        logger.exception("Трей-иконка упала с исключением")


if __name__ == "__main__":
    run_daemon()