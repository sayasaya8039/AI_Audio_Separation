# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for AI Audio Separation

ビルドコマンド:
    pyinstaller ai_audio_separation.spec

出力: AI_Audio_Separation/AI_Audio_Separation.exe
"""

import sys
from pathlib import Path

block_cipher = None

# プロジェクトルート
PROJECT_ROOT = Path(SPECPATH)

import os

# Demucsパッケージのパス
demucs_path = None
try:
    import demucs
    demucs_path = os.path.dirname(demucs.__file__)
except ImportError:
    pass

a = Analysis(
    ['src/main.py'],
    pathex=[str(PROJECT_ROOT)],
    binaries=[],
    datas=[
        # Demucsのデータファイル（必須）
        (os.path.join(demucs_path, 'remote'), 'demucs/remote'),
    ] if demucs_path else [],
    hiddenimports=[
        # PyTorch関連
        'torch',
        'torchaudio',
        'torchaudio.transforms',
        'torchaudio.functional',
        # Demucs
        'demucs',
        'demucs.pretrained',
        'demucs.apply',
        # オーディオ処理
        'sounddevice',
        'soundfile',
        'librosa',
        'librosa.effects',
        # GUI
        'PyQt6',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'pyqtgraph',
        # その他
        'numpy',
        'scipy',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # 不要なモジュールを除外してサイズ削減
        'tkinter',
        'matplotlib',
        'IPython',
        'jupyter',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='AI_Audio_Separation',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # GUIアプリなのでコンソールを非表示
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # アイコンファイルがあれば指定: 'resources/icon.ico'
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='AI_Audio_Separation',
)
