import subprocess


class GoBridge:
    def __init__(self, binary_path="./encoder"):
        self.binary_path = binary_path

    def run_split(self, file_path, data_blocks, parity_blocks, target_dirs: list):
        dirs_str = ",".join(target_dirs)
        cmd = [
            self.binary_path,
            "-mode=split",
            f"-file={file_path}",
            f"-data={data_blocks}",
            f"-parity={parity_blocks}",
            f"-dirs={dirs_str}"
        ]
        return self._execute(cmd)

    def run_join(self, base_name, out_file_path, source_dirs: list):
        """
        base_name — имя файла для поиска шардов (например 'bg_dark.jpg'),
        то самое, что вернул DiscoveryService.
        K/M больше не нужны — Go сам возьмёт их из манифеста на диске.
        """
        dirs_str = ",".join(source_dirs)
        cmd = [
            self.binary_path,
            "-mode=join",
            f"-basename={base_name}",
            f"-out={out_file_path}",
            f"-dirs={dirs_str}"
        ]
        return self._execute(cmd)

    def _execute(self, cmd):
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8")
        if result.returncode != 0:
            raise Exception(result.stderr if result.stderr else result.stdout)
        return result.stdout