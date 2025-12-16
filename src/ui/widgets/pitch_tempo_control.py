"""
ピッチ・テンポコントロールウィジェット
"""

from typing import Optional

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)


class PitchTempoControl(QFrame):
    """
    ピッチ・テンポコントロールウィジェット

    ピッチシフト（±12半音）とテンポ変更（50%〜200%）
    """

    # シグナル
    pitch_changed = pyqtSignal(float)  # 半音単位
    tempo_changed = pyqtSignal(float)  # 比率（1.0 = 100%）

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setProperty("class", "card")

        self._setup_ui()

    def _setup_ui(self) -> None:
        """UIをセットアップ"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(24)

        # ピッチコントロール
        pitch_layout = QVBoxLayout()
        pitch_layout.setSpacing(4)

        pitch_header = QHBoxLayout()
        pitch_icon = QLabel("[P]")
        pitch_icon.setStyleSheet("font-size: 14px; font-weight: bold;")
        pitch_label = QLabel("ピッチ")
        pitch_label.setStyleSheet("font-weight: bold;")
        pitch_header.addWidget(pitch_icon)
        pitch_header.addWidget(pitch_label)
        pitch_header.addStretch()
        pitch_layout.addLayout(pitch_header)

        pitch_slider_layout = QHBoxLayout()
        self._pitch_slider = QSlider(Qt.Orientation.Horizontal)
        self._pitch_slider.setRange(-12, 12)
        self._pitch_slider.setValue(0)
        self._pitch_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self._pitch_slider.setTickInterval(6)
        self._pitch_slider.valueChanged.connect(self._on_pitch_changed)

        self._pitch_value = QLabel("±0")
        self._pitch_value.setMinimumWidth(40)
        self._pitch_value.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        pitch_slider_layout.addWidget(self._pitch_slider, 1)
        pitch_slider_layout.addWidget(self._pitch_value)
        pitch_layout.addLayout(pitch_slider_layout)

        pitch_range = QLabel("-12 ←→ +12 半音")
        pitch_range.setProperty("class", "subtitle")
        pitch_range.setStyleSheet("color: #94A3B8; font-size: 11px;")
        pitch_layout.addWidget(pitch_range)

        # リセットボタン（右寄せ用レイアウト）
        pitch_reset_layout = QHBoxLayout()
        pitch_reset_layout.addStretch()
        self._pitch_reset = QPushButton("リセット")
        self._pitch_reset.setFixedSize(80, 32)
        self._pitch_reset.clicked.connect(lambda: self._pitch_slider.setValue(0))
        pitch_reset_layout.addWidget(self._pitch_reset)
        pitch_layout.addLayout(pitch_reset_layout)

        layout.addLayout(pitch_layout, 1)

        # 区切り線
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.VLine)
        separator.setStyleSheet("background-color: #334155;")
        layout.addWidget(separator)

        # テンポコントロール
        tempo_layout = QVBoxLayout()
        tempo_layout.setSpacing(4)

        tempo_header = QHBoxLayout()
        tempo_icon = QLabel("[T]")
        tempo_icon.setStyleSheet("font-size: 14px; font-weight: bold;")
        tempo_label = QLabel("テンポ")
        tempo_label.setStyleSheet("font-weight: bold;")
        tempo_header.addWidget(tempo_icon)
        tempo_header.addWidget(tempo_label)
        tempo_header.addStretch()
        tempo_layout.addLayout(tempo_header)

        tempo_slider_layout = QHBoxLayout()
        self._tempo_slider = QSlider(Qt.Orientation.Horizontal)
        self._tempo_slider.setRange(50, 200)
        self._tempo_slider.setValue(100)
        self._tempo_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self._tempo_slider.setTickInterval(50)
        self._tempo_slider.valueChanged.connect(self._on_tempo_changed)

        self._tempo_value = QLabel("100%")
        self._tempo_value.setMinimumWidth(45)
        self._tempo_value.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        tempo_slider_layout.addWidget(self._tempo_slider, 1)
        tempo_slider_layout.addWidget(self._tempo_value)
        tempo_layout.addLayout(tempo_slider_layout)

        tempo_range = QLabel("50% ←→ 200%")
        tempo_range.setProperty("class", "subtitle")
        tempo_range.setStyleSheet("color: #94A3B8; font-size: 11px;")
        tempo_layout.addWidget(tempo_range)

        # リセットボタン（右寄せ用レイアウト）
        tempo_reset_layout = QHBoxLayout()
        tempo_reset_layout.addStretch()
        self._tempo_reset = QPushButton("リセット")
        self._tempo_reset.setFixedSize(80, 32)
        self._tempo_reset.clicked.connect(lambda: self._tempo_slider.setValue(100))
        tempo_reset_layout.addWidget(self._tempo_reset)
        tempo_layout.addLayout(tempo_reset_layout)

        layout.addLayout(tempo_layout, 1)

    def _on_pitch_changed(self, value: int) -> None:
        """ピッチスライダー変更時"""
        if value > 0:
            self._pitch_value.setText(f"+{value}")
        elif value < 0:
            self._pitch_value.setText(str(value))
        else:
            self._pitch_value.setText("±0")
        self.pitch_changed.emit(float(value))

    def _on_tempo_changed(self, value: int) -> None:
        """テンポスライダー変更時"""
        self._tempo_value.setText(f"{value}%")
        self.tempo_changed.emit(value / 100.0)

    def pitch(self) -> float:
        """ピッチ値を取得（半音単位）"""
        return float(self._pitch_slider.value())

    def set_pitch(self, semitones: float) -> None:
        """ピッチを設定"""
        self._pitch_slider.setValue(int(semitones))

    def tempo(self) -> float:
        """テンポ値を取得（比率）"""
        return self._tempo_slider.value() / 100.0

    def set_tempo(self, ratio: float) -> None:
        """テンポを設定"""
        self._tempo_slider.setValue(int(ratio * 100))

    def reset(self) -> None:
        """値をリセット"""
        self._pitch_slider.setValue(0)
        self._tempo_slider.setValue(100)

    def set_enabled(self, enabled: bool) -> None:
        """コントロールの有効/無効を設定"""
        self._pitch_slider.setEnabled(enabled)
        self._tempo_slider.setEnabled(enabled)
        self._pitch_reset.setEnabled(enabled)
        self._tempo_reset.setEnabled(enabled)
