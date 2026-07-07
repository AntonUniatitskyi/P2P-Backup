import os


class Config:
    DEFAULT_DATA_SHARDS = 3
    DEFAULT_PARITY_SHARDS = 2

    SIMULATED_DIR = "./simulated_flashes"
    GO_BINARY_PATH = "./encoder"  # На Windows будет "encoder.exe"

    # Настройки UI
    APP_TITLE = "P2P Flash Raid / Локальный бэкапер"
    WINDOW_WIDTH = 700
    WINDOW_HEIGHT = 600

    @classmethod
    def ensure_directories(cls):
        """Создает необходимые папки при старте"""
        os.makedirs(cls.SIMULATED_DIR, exist_ok=True)