import json
import os
from pathlib import Path

INDEX_PATH = Path(os.getenv("LOCALAPPDATA")) / "P2PBackup" / "index.json"


class ShardIndex:
    """
    Персистентный реестр: какие манифесты/шарды мы когда-либо видели
    и на каком именно томе (по серийному номеру, не по букве диска).
    """

    def __init__(self):
        INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
        self.data = self._load()

    def _load(self):
        if INDEX_PATH.exists():
            try:
                return json.loads(INDEX_PATH.read_text(encoding="utf-8"))
            except Exception:
                pass
        return {"files": {}, "recovered": []}

    def save(self):
        INDEX_PATH.write_text(json.dumps(self.data, indent=2, ensure_ascii=False), encoding="utf-8")

    def register_shard(self, basename: str, shard_index: int, volume_serial: str):
        entry = self.data["files"].setdefault(basename, {"shards": {}, "manifest": None})
        entry["shards"][str(shard_index)] = volume_serial

    def register_manifest(self, basename: str, manifest: dict):
        entry = self.data["files"].setdefault(basename, {"shards": {}, "manifest": None})
        entry["manifest"] = manifest

    def mark_recovered(self, basename: str, path: str):
        self.data["recovered"].append({"basename": basename, "path": path})

    def is_recovered(self, basename: str) -> bool:
        return any(r["basename"] == basename for r in self.data["recovered"])

    def candidates_ready(self, mounted_serials: set[str]):
        """
        Возвращает список basename, для которых среди ТЕКУЩЕ подключённых
        томов достаточно шардов, чтобы восстановить (K штук).
        """
        ready = []
        for basename, entry in self.data["files"].items():
            manifest = entry.get("manifest")
            if not manifest or self.is_recovered(basename):
                continue

            k = manifest["data_shards"]
            available_now = [
                idx for idx, serial in entry["shards"].items()
                if serial in mounted_serials
            ]
            if len(available_now) >= k:
                ready.append(basename)
        return ready