# -*- mode: python ; coding: utf-8 -*-
a = Analysis(
    ['../manager-python/app/launch_daemon.py'],
    pathex=['../manager-python'],
    binaries=[('../manager-python/encoder.exe', '.')],
    datas=[],
    hiddenimports=['win32timezone', 'pystray._win32'],
    hookspath=[],
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz, a.scripts, a.binaries, a.datas,
    name='P2PBackupDaemon',
    console=False,
    icon='../assets/icon.ico',
)