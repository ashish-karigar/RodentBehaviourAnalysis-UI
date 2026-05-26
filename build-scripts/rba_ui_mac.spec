# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_submodules

block_cipher = None

hiddenimports = (
    collect_submodules("PyQt6")
    + collect_submodules("src")
    + [
        "requests",
        "dotenv",
    ]
)

a = Analysis(
    ["../rba_ui_entry.py"],
    pathex=[".."],
    binaries=[],
    datas=[
        ("../assets", "assets"),
        ("../.env", "."),
    ],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher,
)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="RodentBehaviourAnalysisUI",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="RodentBehaviourAnalysisUI",
)

app = BUNDLE(
    coll,
    name="RodentBehaviourAnalysisUI.app",
    icon="../assets/icons/app_icon.icns",
    bundle_identifier="com.rodentbehaviouranalysis.ui",
)