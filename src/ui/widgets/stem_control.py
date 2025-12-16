"""
ステムコントロールウィジェット

各ステム（Vocals, Drums, Bass, Other）のボリューム・ミュート・ソロを管理
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

from src.ui.theme import ThemeManager


class StemControl(QFrame):
    """
    ステムコントロールウィジェット

    ボリュームスライダー、ミュート/ソロボタンを含む
    """

    # シグナル
    volume_changed = pyqtSignal(str, float)  # (ステム名, ボリューム)
    mute_toggled = pyqtSignal(str, bool)  # (ステム名, ミュート状態)
    solo_toggled = pyqtSignal(str, bool)  # (ステム名, ソロ状態)

    # ステムの表示名とアイコン
    STEM_INFO = {
        "vocals": ("Vocals", "[V]"),
        "drums": ("Drums", "[D]"),
        "bass": ("Bass", "[B]"),
        "other": ("Other", "[O]"),
    }

    def __init__(
        self,
        stem_name: str,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        self._stem_name = stem_name
        self._muted = False
        self._solo = False

        self._setup_ui()
        self._apply_stem_style()

    def _setup_ui(self) -> None:
        """UIをセットアップ"""
        self.setProperty("class", "card")
        self.setProperty("stem", self._stem_name)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        # ステム名とアイコン
        display_name, icon = self.STEM_INFO.get(
            self._stem_name, (self._stem_name.capitalize(), "[*]")
        )

        header_layout = QHBoxLayout()
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        name_label = QLabel(display_name)
        name_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        header_layout.addWidget(icon_label)
        header_layout.addWidget(name_label)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        # ボリュームスライダー
        slider_layout = QHBoxLayout()
        self._volume_slider = QSlider(Qt.Orientation.Horizontal)
        self._volume_slider.setRange(0, 100)
        self._volume_slider.setValue(100)
        self._volume_slider.valueChanged.connect(self._on_volume_changed)

        self._volume_label = QLabel("100%")
        self._volume_label.setMinimumWidth(45)
        self._volume_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        slider_layout.addWidget(self._volume_slider, 1)
        slider_layout.addWidget(self._volume_label)
        layout.addLayout(slider_layout)

        # ミュート/ソロボタン
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)

        self._mute_btn = QPushButton("M")
        self._mute_btn.setProperty("class", "icon-button")
        self._mute_btn.setCheckable(True)
        self._mute_btn.setToolTip("ミュート")
        self._mute_btn.setFixedSize(36, 36)
        self._mute_btn.clicked.connect(self._on_mute_clicked)

        self._solo_btn = QPushButton("S")
        self._solo_btn.setProperty("class", "icon-button")
        self._solo_btn.setCheckable(True)
        self._solo_btn.setToolTip("ソロ")
        self._solo_btn.setFixedSize(36, 36)
        self._solo_btn.clicked.connect(self._on_solo_clicked)

        button_layout.addWidget(self._mute_btn)
        button_layout.addWidget(self._solo_btn)
        button_layout.addStretch()
        layout.addLayout(button_layout)

        self.setMinimumWidth(140)
        self.setMaximumWidth(180)

    def _apply_stem_style(self) -> None:
        """ステム固有のスタイルを適用"""
        theme = ThemeManager()
        color = theme.get_stem_color(self._stem_name)
        self.setStyleSheet(f"QFrame {{ border-left: 4px solid {color}; }}")

    def _on_volume_changed(self, value: int) -> None:
        """ボリューム変更時"""
        self._volume_label.setText(f"{value}%")
        self.volume_changed.emit(self._stem_name, value / 100.0)

    def _on_mute_clicked(self) -> None:
        """ミュートボタンクリック時"""
        self._muted = self._mute_btn.isChecked()
        self.mute_toggled.emit(self._stem_name, self._muted)

    def _on_solo_clicked(self) -> None:
        """ソロボタンクリック時"""
        self._solo = self._solo_btn.isChecked()
        self.solo_toggled.emit(self._stem_name, self._solo)

    @property
    def stem_name(self) -> str:
        """ステム名を取得"""
        return self._stem_name

    def volume(self) -> float:
        """ボリュームを取得（0.0〜1.0）"""
        return self._volume_slider.value() / 100.0

    def set_volume(self, value: float) -> None:
        """ボリュームを設定"""
        self._volume_slider.setValue(int(value * 100))

    def is_muted(self) -> bool:
        """ミュート状態を取得"""
        return self._muted

    def set_muted(self, muted: bool) -> None:
        """ミュート状態を設定"""
        self._muted = muted
        self._mute_btn.setChecked(muted)

    def is_solo(self) -> bool:
        """ソロ状態を取得"""
        return self._solo

    def set_solo(self, solo: bool) -> None:
        """ソロ状態を設定"""
        self._solo = solo
        self._solo_btn.setChecked(solo)

    def reset(self) -> None:
        """状態をリセット"""
        self._volume_slider.setValue(100)
        self._mute_btn.setChecked(False)
        self._solo_btn.setChecked(False)
        self._muted = False
        self._solo = False
