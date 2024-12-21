# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['ui\\MainGUI.py'],
    pathex=['ui'],
    binaries=[('D:\\ffmpeg-N-116133-g03175b587c-win64-gpl\\bin\\ffmpeg.exe', '.'),('D:\\ffmpeg-N-116133-g03175b587c-win64-gpl\\bin\\ffprobe.exe', '.')],
    datas=[("E:\\__PythonProject__\\L4D2AudioTranformer_All\\dicGenerate\\*.db", "dicGenerate"),("blank_audio.wav",".")],
    hiddenimports=['ffmpeg', 'PySide6'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='L4D2AudioTranformer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    icon=None,
    onefile=True
)