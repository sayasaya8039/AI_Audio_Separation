"""
トランスポートバー（再生コントロール）

再生/一時停止、シークバー、時間表示
"""

from typing import Optional

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)


class TransportBar(QWidget):
    """
    トランスポートバー

    再生コントロールとシークバーを提供
    """

    # シグナル
    play_clicked = pyqtSignal()
    pause_clicked = pyqtSignal()
    stop_clicked = pyqtSignal()
    seek_requested = pyqtSignal(float)  # 位置（秒）
    skip_forward = pyqtSignal()
    skip_backward = pyqtSignal()

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._is_playing = False
        self._duration = 0.0
        self._seeking = False

        self._setup_ui()

    def _setup_ui(self) -> None:
        """UIをセットアップ"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # シークバーと時間表示
        seek_layout = QHBoxLayout()
        seek_layout.setSpacing(12)

        self._current_time = QLabel("00:00")
        self._current_time.setMinimumWidth(50)

        self._seek_slider = QSlider(Qt.Orientation.Horizontal)
        self._seek_slider.setRange(0, 1000)
        self._seek_slider.setValue(0)
        self._seek_slider.sliderPressed.connect(self._on_seek_pressed)
        self._seek_slider.sliderReleased.connect(self._on_seek_released)
        self._seek_slider.valueChanged.connect(self._on_seek_value_changed)

        self._total_time = QLabel("00:00")
        self._total_time.setMinimumWidth(50)
        self._total_time.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        seek_layout.addWidget(self._current_time)
        seek_layout.addWidget(self._seek_slider, 1)
        seek_layout.addWidget(self._total_time)
        layout.addLayout(seek_layout)

        # 再生コントロールボタン
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(16)
        controls_layout.addStretch()

        # 前へスキップ
        self._skip_back_btn = QPushButton("⏮")
        self._skip_back_btn.setFixedSize(40, 40)
        self._skip_back_btn.setToolTip("10秒戻る")
        self._skip_back_btn.clicked.connect(self.skip_backward.emit)

        # 巻き戻し
        self._rewind_btn = QPushButton("⏪")
        self._rewind_btn.setFixedSize(40, 40)
        self._rewind_btn.setToolTip("5秒戻る")
        self._rewind_btn.clicked.connect(lambda: self.skip_backward.emit())

        # 再生/一時停止
        self._play_btn = QPushButton("▶")
        self._play_btn.setFixedSize(56, 56)
        self._play_btn.setToolTip("再生")
        self._play_btn.clicked.connect(self._on_play_clicked)
        self._play_btn.setStyleSheet("font-size: 24px;")

        # 早送り
        self._forward_btn = QPushButton("⏩")
        self._forward_btn.setFixedSize(40, 40)
        self._forward_btn.setToolTip("5秒進む")
        self._forward_btn.clicked.connect(lambda: self.skip_forward.emit())

        # 次へスキップ
        self._skip_fwd_btn = QPushButton("⏭")
        self._skip_fwd_btn.setFixedSize(40, 40)
        self._skip_fwd_btn.setToolTip("10秒進む")
        self._skip_fwd_btn.clicked.connect(self.skip_forward.emit)

        # 停止
        self._stop_btn = QPushButton("⏹")
        self._stop_btn.setFixedSize(40, 40)
        self._stop_btn.setToolTip("停止")
        self._stop_btn.clicked.connect(self._on_stop_clicked)

        controls_layout.addWidget(self._skip_back_btn)
        controls_layout.addWidget(self._rewind_btn)
        controls_layout.addWidget(self._play_btn)
        controls_layout.addWidget(self._forward_btn)
        controls_layout.addWidget(self._skip_fwd_btn)
        controls_layout.addWidget(self._stop_btn)
        controls_layout.addStretch()

        layout.addLayout(controls_layout)

    def _on_play_clicked(self) -> None:
        """再生ボタンクリック時"""
        if self._is_playing:
            self.pause_clicked.emit()
        else:
            self.play_clicked.emit()

    def _on_stop_clicked(self) -> None:
        """停止ボタンクリック時"""
        self.stop_clicked.emit()

    def _on_seek_pressed(self) -> None:
        """シーク開始"""
        self._seeking = True

    def _on_seek_released(self) -> None:
        """シーク終了"""
        self._seeking = False
        if self._duration > 0:
            position = (self._seek_slider.value() / 1000.0) * self._duration
            self.seek_requested.emit(position)

    def _on_seek_value_changed(self, value: int) -> None:
        """シークバー値変更時"""
        if self._seeking and self._duration > 0:
            position = (value / 1000.0) * self._duration
            self._current_time.setText(self._format_time(position))

    def set_playing(self, playing: bool) -> None:
        """再生状態を設定"""
        self._is_playing = playing
        self._play_btn.setText("⏸" if playing else "▶")
        self._play_btn.setToolTip("一時停止" if playing else "再生")

    def set_duration(self, duration: float) -> None:
        """総再生時間を設定"""
        self._duration = duration
        self._total_time.setText(self._format_time(duration))

    def set_position(self, position: float) -> None:
        """現在位置を設定"""
        if not self._seeking:
            self._current_time.setText(self._format_time(position))
            if self._duration > 0:
                slider_value = int((position / self._duration) * 1000)
                self._seek_slider.setValue(slider_value)

    def reset(self) -> None:
        """状態をリセット"""
        self._is_playing = False
        self._duration = 0.0
        self._play_btn.setText("▶")
        self._current_time.setText("00:00")
        self._total_time.setText("00:00")
        self._seek_slider.setValue(0)

    @staticmethod
    def _format_time(seconds: float) -> str:
        """時間をフォーマット（MM:SS）"""
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"

    def set_enabled(self, enabled: bool) -> None:
        """コントロールの有効/無効を設定"""
        self._play_btn.setEnabled(enabled)
        self._stop_btn.setEnabled(enabled)
        self._skip_back_btn.setEnabled(enabled)
        self._skip_fwd_btn.setEnabled(enabled)
        self._rewind_btn.setEnabled(enabled)
        self._forward_btn.setEnabled(enabled)
        self._seek_slider.setEnabled(enabled)
