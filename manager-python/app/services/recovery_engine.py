import json
import logging
import os
from pathlib import Path

from app.services.shard_index import ShardIndex, INDEX_PATH
from app.services.go_bridge import GoBridge

READY_DIR = INDEX_PATH.parent / "ready"
logger = logging.getLogger("p2p-backup-daemon.recovery")


class RecoveryEngine:
    def __init__(self, go_binary_path, on_file_ready=None):
        self.bridge = GoBridge(go_binary_path)
        self.index = ShardIndex()
        self.on_file_ready = on_file_ready or (lambda name, path: None)
        READY_DIR.mkdir(parents=True, exist_ok=True)

    def scan_drive(self, serial: str, drive_path: str):
        """Сканирует корень диска на предмет .shard.* и .meta файлов."""
        logger.info(f"Сканирую диск {drive_path} (serial={serial})")

        try:
            entries = os.listdir(drive_path)
        except Exception as ex:
            logger.warning(f"Не удалось прочитать {drive_path}: {ex}")
            return

        manifests_found = 0
        shards_found = 0

        for entry in entries:
            full_path = os.path.join(drive_path, entry)

            if entry.endswith(".meta"):
                basename = entry[: -len(".meta")]
                try:
                    manifest = json.loads(Path(full_path).read_text(encoding="utf-8"))
                    self.index.register_manifest(basename, manifest)
                    manifests_found += 1
                except Exception as ex:
                    logger.warning(f"Битый манифест {full_path}: {ex}")
                    continue

            elif ".shard." in entry:
                basename, _, shard_num = entry.rpartition(".shard.")
                try:
                    shard_idx = int(shard_num)
                    self.index.register_shard(basename, shard_idx, serial)
                    shards_found += 1
                except ValueError:
                    logger.warning(f"Не удалось распознать номер шарда: {entry}")
                    continue

        self.index.save()
        logger.info(f"Диск {drive_path}: найдено манифестов={manifests_found}, шардов={shards_found}")

    def try_recover_ready_files(self, mounted_serials: set[str], mounted_map: dict[str, str]):
        ready_basenames = self.index.candidates_ready(mounted_serials)

        if not ready_basenames:
            logger.debug("Нет файлов, готовых к восстановлению на текущий момент")
            return

        for basename in ready_basenames:
            entry = self.index.data["files"][basename]
            # собираем список путей дисков, где есть шарды этого файла — прямо сейчас подключённых
            source_dirs = {
                mounted_map[serial]
                for idx, serial in entry["shards"].items()
                if serial in mounted_serials
            }

            logger.info(f"Найдено достаточно кусков для '{basename}', пробую восстановить "
                        f"(источники: {', '.join(source_dirs)})...")
            out_path = str(READY_DIR / f"restored_{basename}")

            try:
                output = self.bridge.run_join(basename, out_path, list(source_dirs))
                logger.debug(f"Вывод Go-ядра для '{basename}': {output}")

                self.index.mark_recovered(basename, out_path)
                self.index.save()
                logger.info(f"Готово: {basename} -> {out_path}")
                self.on_file_ready(basename, out_path)
            except Exception:
                logger.exception(f"Не удалось собрать '{basename}'")

    def handle_drives_changed(self, current: dict, added: dict, removed: set):
        if added:
            logger.info(f"Подключены новые тома: {list(added.values())}")
        if removed:
            logger.info(f"Отключены тома: {removed}")

        for serial, path in added.items():
            self.scan_drive(serial, path)

        self.try_recover_ready_files(set(current.keys()), current)