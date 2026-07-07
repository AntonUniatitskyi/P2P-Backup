import psutil


def get_mounted_flash_drives():
    flash_drives = []
    partitions = psutil.disk_partitions(all=False)

    for p in partitions:
        if 'removable' in p.opts or '/media/' in p.mountpoint or '/Volumes/' in p.mountpoint:
            flash_drives.append(p.mountpoint)

    return flash_drives