"""
ステムミキサーUI

4つのステムコントロールを並べて表示
"""

from typing import Dict, Optional

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QHBoxLayout, QWidget

from src.ui.widgets.stem_control import StemControl


class StemMixerUI(QWidget):
    """
    ステムミキサーUI

    Vocals, Drums, Bass, Otherの4つのステムコントロールを表示
    """

    # シグナル
    volume_changed = pyqtSignal(str, float)
    mute_toggled = pyqtSignal(str, bool)
    solo_toggled = pyqtSignal(str, bool)

    STEM_NAMES = ["vocals", "drums", "bass", "other"]

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._controls: Dict[str, StemControl] = {}

        self._setup_ui()

    def _setup_ui(self) -> None:
        """UIをセットアップ"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        # 各ステムのコントロールを作成
        for stem_name in self.STEM_NAMES:
            control = StemControl(stem_name, self)
            control.volume_changed.connect(self.volume_changed.emit)
            control.mute_toggled.connect(self.mute_toggled.emit)
            control.solo_toggled.connect(self.solo_toggled.emit)

            self._controls[stem_name] = control
            layout.addWidget(control)

        layout.addStretch()

    def get_control(self, stem_name: str) -> Optional[StemControl]:
        """ステムコントロールを取得"""
        return self._controls.get(stem_name)

    def set_volume(self, stem_name: str, volume: float) -> None:
        """ステムのボリュームを設定"""
        if stem_name in self._controls:
            self._controls[stem_name].set_volume(volume)

    def set_muted(self, stem_name: str, muted: bool) -> None:
        """ステムのミュートを設定"""
        if stem_name in self._controls:
            self._controls[stem_name].set_muted(muted)

    def set_solo(self, stem_name: str, solo: bool) -> None:
        """ステムのソロを設定"""
        if stem_name in self._controls:
            self._controls[stem_name].set_solo(solo)

    def get_volumes(self) -> Dict[str, float]:
        """全ステムのボリュームを取得"""
        return {
            name: control.volume()
            for name, control in self._controls.items()
        }

    def get_mutes(self) -> Dict[str, bool]:
        """全ステムのミュート状態を取得"""
        return {
            name: control.is_muted()
            for name, control in self._controls.items()
        }

    def get_solos(self) -> Dict[str, bool]:
        """全ステムのソロ状態を取得"""
        return {
            name: control.is_solo()
            for name, control in self._controls.items()
        }

    def reset_all(self) -> None:
        """全ステムをリセット"""
        for control in self._controls.values():
            control.reset()

    def set_enabled(self, enabled: bool) -> None:
        """全コントロールの有効/無効を設定"""
        for control in self._controls.values():
            control.setEnabled(enabled)
