"""
波形表示ウィジェット

pyqtgraphを使用したリアルタイム波形表示
"""

from typing import Dict, Optional

import numpy as np
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QVBoxLayout, QWidget

try:
    import pyqtgraph as pg
    PYQTGRAPH_AVAILABLE = True
except ImportError:
    PYQTGRAPH_AVAILABLE = False

from src.ui.theme import ThemeManager


class WaveformView(QWidget):
    """
    波形表示ウィジェット

    オーディオの波形を表示し、再生位置を示す
    """

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._audio_data: Optional[np.ndarray] = None
        self._sample_rate: int = 44100
        self._position: float = 0.0
        self._duration: float = 0.0

        self._setup_ui()

    def _setup_ui(self) -> None:
        """UIをセットアップ"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        if PYQTGRAPH_AVAILABLE:
            # pyqtgraph設定
            pg.setConfigOptions(antialias=True)

            theme = ThemeManager()
            colors = theme.colors

            # プロットウィジェット作成
            self._plot_widget = pg.PlotWidget()
            self._plot_widget.setBackground(colors.background_sub)
            self._plot_widget.setMinimumHeight(120)
            self._plot_widget.showGrid(x=False, y=False)
            self._plot_widget.hideAxis("left")
            self._plot_widget.hideAxis("bottom")
            self._plot_widget.setMouseEnabled(x=False, y=False)

            # 波形プロット
            self._waveform_plot = self._plot_widget.plot(
                pen=pg.mkPen(color=colors.accent, width=1)
            )

            # 再生位置インジケータ
            self._position_line = pg.InfiniteLine(
                pos=0,
                angle=90,
                pen=pg.mkPen(color="#F87171", width=2),
            )
            self._plot_widget.addItem(self._position_line)

            layout.addWidget(self._plot_widget)
        else:
            # pyqtgraphがない場合のフォールバック
            from PyQt6.QtWidgets import QLabel
            placeholder = QLabel("波形表示（pyqtgraphが必要です）")
            placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            placeholder.setMinimumHeight(120)
            placeholder.setStyleSheet("background-color: #1E293B; border-radius: 8px;")
            layout.addWidget(placeholder)
            self._plot_widget = None
            self._waveform_plot = None
            self._position_line = None

    def set_audio(self, audio: np.ndarray, sample_rate: int) -> None:
        """
        オーディオデータを設定

        Args:
            audio: オーディオデータ（1D配列）
            sample_rate: サンプルレート
        """
        self._audio_data = audio
        self._sample_rate = sample_rate
        self._duration = len(audio) / sample_rate if sample_rate > 0 else 0.0

        self._update_waveform()

    def _update_waveform(self) -> None:
        """波形を更新"""
        if not PYQTGRAPH_AVAILABLE or self._waveform_plot is None:
            return

        if self._audio_data is None or len(self._audio_data) == 0:
            self._waveform_plot.setData([], [])
            return

        # ダウンサンプリング（表示用に間引き）
        target_points = 2000
        step = max(1, len(self._audio_data) // target_points)

        # エンベロープを計算（最大値と最小値）
        downsampled = self._audio_data[::step]

        # 時間軸
        x = np.linspace(0, self._duration, len(downsampled))

        self._waveform_plot.setData(x, downsampled)
        self._plot_widget.setXRange(0, self._duration, padding=0)
        self._plot_widget.setYRange(-1, 1, padding=0.1)

    def set_position(self, seconds: float) -> None:
        """
        再生位置を設定

        Args:
            seconds: 位置（秒）
        """
        self._position = seconds
        if self._position_line is not None:
            self._position_line.setPos(seconds)

    def clear(self) -> None:
        """波形をクリア"""
        self._audio_data = None
        self._position = 0.0
        self._duration = 0.0

        if self._waveform_plot is not None:
            self._waveform_plot.setData([], [])

        if self._position_line is not None:
            self._position_line.setPos(0)

    def set_stems_overlay(self, stems: Dict[str, np.ndarray], sample_rate: int) -> None:
        """
        複数ステムのオーバーレイ表示

        Args:
            stems: ステム名 -> オーディオデータの辞書
            sample_rate: サンプルレート
        """
        if not PYQTGRAPH_AVAILABLE or self._plot_widget is None:
            return

        # 既存のプロットをクリア
        self._plot_widget.clear()
        self._plot_widget.addItem(self._position_line)

        theme = ThemeManager()

        # 各ステムを色分けして表示
        for stem_name, audio in stems.items():
            if audio is None or len(audio) == 0:
                continue

            color = theme.get_stem_color(stem_name)

            # ダウンサンプリング
            target_points = 1000
            step = max(1, len(audio) // target_points)
            downsampled = audio[::step]

            # 時間軸
            duration = len(audio) / sample_rate
            x = np.linspace(0, duration, len(downsampled))

            # プロット追加
            self._plot_widget.plot(
                x, downsampled,
                pen=pg.mkPen(color=color, width=1),
                name=stem_name,
            )

        self._duration = max(
            len(a) / sample_rate for a in stems.values() if a is not None and len(a) > 0
        ) if stems else 0.0

        self._plot_widget.setXRange(0, self._duration, padding=0)
        self._plot_widget.setYRange(-1, 1, padding=0.1)

    def update_theme(self) -> None:
        """テーマ変更時に更新"""
        if not PYQTGRAPH_AVAILABLE or self._plot_widget is None:
            return

        theme = ThemeManager()
        colors = theme.colors

        self._plot_widget.setBackground(colors.background_sub)

        if self._waveform_plot is not None:
            self._waveform_plot.setPen(pg.mkPen(color=colors.accent, width=1))
