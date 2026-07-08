# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_all

datas = []
binaries = []
hiddenimports = []

for pkg in ['flet', 'flet_desktop']:
    pkg_datas, pkg_binaries, pkg_hiddenimports = collect_all(pkg)
    datas += pkg_datas
    binaries += pkg_binaries
    hiddenimports += pkg_hiddenimports
    
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