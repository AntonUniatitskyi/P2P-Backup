import os
import sys


def _resource_path(relative_path: str) -> str:
    if hasattr(sys, "_MEIPASS"):
        base_path = sys._MEIPASS
    else:
        # app/config.py -> manager-python/
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


class Config:
    DEFAULT_DATA_SHARDS = 3
    DEFAULT_PARITY_SHARDS = 2

    SIMULATED_DIR = "./simulated_flashes"
    GO_BINARY_PATH = _resource_path("encoder.exe" if sys.platform == "win32" else "encoder")

    # Настройки UI
    APP_TITLE = "P2P Flash Raid / Локальный бэкапер"
    WINDOW_WIDTH = 700
    WINDOW_HEIGHT = 600

    @classmethod
    def ensure_directories(cls):
        """Создает необходимые папки при старте"""
        os.makedirs(cls.SIMULATED_DIR, exist_ok=True)