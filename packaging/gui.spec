# -*- mode: python ; coding: utf-8 -*-
a = Analysis(
    ['../manager-python/app/launch_gui.py'],
    pathex=['../manager-python'],
    binaries=[('../manager-python/encoder.exe', '.')],
    datas=[],
    hiddenimports=['flet'],
    hookspath=[],
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz, a.scripts, a.binaries, a.datas,
    name='P2PBackupGUI',
    console=False,          # без консоли — это GUI
    icon='../assets/icon.ico',
)