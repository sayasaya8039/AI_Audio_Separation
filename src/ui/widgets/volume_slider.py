"""
ボリュームスライダーウィジェット
"""

from typing import Optional

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QSlider,
    QVBoxLayout,
    QWidget,
)


class VolumeSlider(QWidget):
    """
    ボリュームスライダー

    縦または横向きのスライダーとパーセント表示
    """

    # シグナル
    value_changed = pyqtSignal(float)  # 0.0〜1.0

    def __init__(
        self,
        orientation: Qt.Orientation = Qt.Orientation.Vertical,
        label: str = "",
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        self._orientation = orientation
        self._label_text = label

        self._setup_ui()

    def _setup_ui(self) -> None:
        """UIをセットアップ"""
        # スライダー作成
        self._slider = QSlider(self._orientation)
        self._slider.setRange(0, 100)
        self._slider.setValue(100)
        self._slider.valueChanged.connect(self._on_slider_changed)

        # パーセント表示ラベル
        self._value_label = QLabel("100%")
        self._value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._value_label.setMinimumWidth(40)

        # レイアウト
        if self._orientation == Qt.Orientation.Vertical:
            layout = QVBoxLayout(self)
            layout.setContentsMargins(4, 4, 4, 4)
            layout.setSpacing(4)

            if self._label_text:
                label = QLabel(self._label_text)
                label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                layout.addWidget(label)

            layout.addWidget(self._slider, 1)
            layout.addWidget(self._value_label)

            self._slider.setMinimumHeight(100)
        else:
            layout = QHBoxLayout(self)
            layout.setContentsMargins(4, 4, 4, 4)
            layout.setSpacing(8)

            if self._label_text:
                label = QLabel(self._label_text)
                layout.addWidget(label)

            layout.addWidget(self._slider, 1)
            layout.addWidget(self._value_label)

            self._slider.setMinimumWidth(100)

    def _on_slider_changed(self, value: int) -> None:
        """スライダー値変更時"""
        self._value_label.setText(f"{value}%")
        self.value_changed.emit(value / 100.0)

    def value(self) -> float:
        """現在の値を取得（0.0〜1.0）"""
        return self._slider.value() / 100.0

    def set_value(self, value: float) -> None:
        """値を設定（0.0〜1.0）"""
        int_value = int(value * 100)
        self._slider.setValue(int_value)

    def set_label(self, text: str) -> None:
        """ラベルを設定"""
        self._label_text = text
