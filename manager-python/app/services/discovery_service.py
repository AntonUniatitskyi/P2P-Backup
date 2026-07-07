import os


class DiscoveryService:
    @staticmethod
    def find_restorable_files(directories):
        """Сканирует список папок и возвращает список уникальных имен файлов"""
        discovered_files = set()

        for directory in directories:
            if not os.path.exists(directory):
                continue

            try:
                for entry in os.listdir(directory):
                    # Ищем файлы, заканчивающиеся на .shard.0
                    # Если нашли shard.0, значит файл точно существует
                    if ".shard.0" in entry:
                        # Отрезаем суффикс .shard.0 и получаем оригинальное имя
                        original_name = entry.split(".shard.0")[0]
                        discovered_files.add(original_name)
            except Exception:
                continue  # Игнорируем ошибки доступа к папкам

        return sorted(list(discovered_files))