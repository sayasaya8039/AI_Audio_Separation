"""
AI Audio Separation - エントリーポイント

Moises Live風のリアルタイムAIオーディオ分離ミュージックリミキサー
"""

import sys
import os
from pathlib import Path

# PyInstaller GUIアプリでstdout/stderrがNoneの場合の対策
# これがないとtqdmやprint文でクラッシュする
if sys.stdout is None:
    sys.stdout = open(os.devnull, 'w')
if sys.stderr is None:
    sys.stderr = open(os.devnull, 'w')

# srcディレクトリをパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from src.app import AudioSeparationApp


def main() -> None:
    """アプリケーションのメインエントリーポイント"""
    # High DPI対応
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName("AI Audio Separation")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("AI Audio Separation")

    # メインウィンドウ作成・表示
    window = AudioSeparationApp()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
