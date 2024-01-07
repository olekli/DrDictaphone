# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['package/launch.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='DrDictaphone',
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
    icon=['package/icon/icon.icns'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='DrDictaphone',
)
app = BUNDLE(
    coll,
    name='DrDictaphone.app',
    icon='package/icon/icon.icns',
    bundle_identifier=None,
    info_plist={
    	'CFBundleDisplayName': 'DrDictaphone',
    	'CFBundleExecutable': 'DrDictaphone',
    	'CFBundleIconFile': 'icon.icns',
    	'CFBundleIdentifier': 'DrDictaphone',
    	'CFBundleInfoDictionaryVersion': '6.0',
    	'CFBundleName': 'DrDictaphone',
    	'CFBundlePackageType': 'APPL',
    	'CFBundleShortVersionString': '0.7.0',
    	'SHighResolutionCapable': True,
      'NSMicrophoneUsageDescription': 'Give mic.'
    }
)
