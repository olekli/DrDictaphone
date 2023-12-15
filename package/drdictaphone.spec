# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['drdictaphone/ui.py'],
    pathex=[],
    binaries=[],
    datas=[
      ('drdictaphone/post_processor', 'post_processor'),
      ('drdictaphone/instructions', 'instructions'),
      ('drdictaphone/tools', 'tools'),
      ('drdictaphone/gpt_model', 'gpt_model'),
      ('drdictaphone/profile', 'profile')
    ],
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
    name='drdictaphone-internal',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='drdictaphone-internal',
)
