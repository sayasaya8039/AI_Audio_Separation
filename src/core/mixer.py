"""
ステムミキサー

各ステムのボリューム、ミュート、ソロを管理
"""

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

import numpy as np
from PyQt6.QtCore import QObject, pyqtSignal


@dataclass
class StemState:
    """ステムの状態"""
    name: str
    volume: float = 1.0
    muted: bool = False
    solo: bool = False
    data: Optional[np.ndarray] = None

    def get_effective_volume(self, any_solo: bool) -> float:
        """実効ボリュームを取得（ソロ/ミュート考慮）"""
        if self.muted:
            return 0.0
        if any_solo and not self.solo:
            return 0.0
        return self.volume


class StemMixer(QObject):
    """
    ステムミキサー

    各ステムのボリューム、ミュート、ソロを管理し、
    ミックスされたオーディオを生成
    """

    # シグナル
    volume_changed = pyqtSignal(str, float)  # (ステム名, ボリューム)
    mute_changed = pyqtSignal(str, bool)  # (ステム名, ミュート状態)
    solo_changed = pyqtSignal(str, bool)  # (ステム名, ソロ状態)
    mix_changed = pyqtSignal()  # ミックスが変更された

    # ステム名
    STEM_NAMES = ["vocals", "drums", "bass", "other"]

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)

        # 各ステムの状態
        self._stems: Dict[str, StemState] = {
            name: StemState(name=name) for name in self.STEM_NAMES
        }

        # マスター設定
        self._master_volume: float = 1.0

    @property
    def master_volume(self) -> float:
        """マスターボリューム"""
        return self._master_volume

    @master_volume.setter
    def master_volume(self, value: float) -> None:
        """マスターボリュームを設定"""
        self._master_volume = np.clip(value, 0.0, 1.0)
        self.mix_changed.emit()

    def load_stems(self, stems: Dict[str, np.ndarray]) -> None:
        """
        ステムデータを読み込み

        Args:
            stems: ステム名 -> オーディオデータの辞書
        """
        for name, data in stems.items():
            if name in self._stems:
                self._stems[name].data = data
        self.mix_changed.emit()

    def clear_stems(self) -> None:
        """全ステムのデータをクリア"""
        for stem in self._stems.values():
            stem.data = None
        self.mix_changed.emit()

    def get_stem(self, name: str) -> Optional[StemState]:
        """ステムの状態を取得"""
        return self._stems.get(name)

    def set_volume(self, name: str, volume: float) -> None:
        """
        ステムのボリュームを設定

        Args:
            name: ステム名
            volume: ボリューム（0.0〜1.0）
        """
        if name in self._stems:
            self._stems[name].volume = np.clip(volume, 0.0, 1.0)
            self.volume_changed.emit(name, self._stems[name].volume)
            self.mix_changed.emit()

    def get_volume(self, name: str) -> float:
        """ステムのボリュームを取得"""
        return self._stems[name].volume if name in self._stems else 1.0

    def set_mute(self, name: str, muted: bool) -> None:
        """
        ステムのミュートを設定

        Args:
            name: ステム名
            muted: ミュート状態
        """
        if name in self._stems:
            self._stems[name].muted = muted
            self.mute_changed.emit(name, muted)
            self.mix_changed.emit()

    def toggle_mute(self, name: str) -> bool:
        """ミュートをトグル"""
        if name in self._stems:
            new_state = not self._stems[name].muted
            self.set_mute(name, new_state)
            return new_state
        return False

    def is_muted(self, name: str) -> bool:
        """ミュート状態を取得"""
        return self._stems[name].muted if name in self._stems else False

    def set_solo(self, name: str, solo: bool) -> None:
        """
        ステムのソロを設定

        Args:
            name: ステム名
            solo: ソロ状態
        """
        if name in self._stems:
            self._stems[name].solo = solo
            self.solo_changed.emit(name, solo)
            self.mix_changed.emit()

    def toggle_solo(self, name: str) -> bool:
        """ソロをトグル"""
        if name in self._stems:
            new_state = not self._stems[name].solo
            self.set_solo(name, new_state)
            return new_state
        return False

    def is_solo(self, name: str) -> bool:
        """ソロ状態を取得"""
        return self._stems[name].solo if name in self._stems else False

    def clear_all_solo(self) -> None:
        """全ステムのソロを解除"""
        for stem in self._stems.values():
            if stem.solo:
                stem.solo = False
                self.solo_changed.emit(stem.name, False)
        self.mix_changed.emit()

    def clear_all_mute(self) -> None:
        """全ステムのミュートを解除"""
        for stem in self._stems.values():
            if stem.muted:
                stem.muted = False
                self.mute_changed.emit(stem.name, False)
        self.mix_changed.emit()

    def reset_all_volumes(self) -> None:
        """全ステムのボリュームをリセット"""
        for stem in self._stems.values():
            stem.volume = 1.0
            self.volume_changed.emit(stem.name, 1.0)
        self._master_volume = 1.0
        self.mix_changed.emit()

    def has_any_solo(self) -> bool:
        """いずれかのステムがソロかどうか"""
        return any(s.solo for s in self._stems.values())

    def get_mix(self, start: int = 0, length: Optional[int] = None) -> np.ndarray:
        """
        ミックスされたオーディオを取得

        Args:
            start: 開始サンプル位置
            length: サンプル数（Noneで全体）

        Returns:
            ミックスされたオーディオデータ
        """
        # 最長のステムを取得
        max_len = 0
        for stem in self._stems.values():
            if stem.data is not None:
                max_len = max(max_len, len(stem.data))

        if max_len == 0:
            return np.zeros(0, dtype=np.float32)

        # 範囲を計算
        if length is None:
            length = max_len - start
        end = min(start + length, max_len)
        actual_length = end - start

        if actual_length <= 0:
            return np.zeros(0, dtype=np.float32)

        # ミックス
        mixed = np.zeros(actual_length, dtype=np.float32)
        any_solo = self.has_any_solo()

        for stem in self._stems.values():
            if stem.data is None:
                continue

            # 実効ボリューム
            effective_vol = stem.get_effective_volume(any_solo)
            if effective_vol <= 0:
                continue

            # データ範囲
            data_end = min(end, len(stem.data))
            data_length = data_end - start
            if data_length <= 0:
                continue

            mixed[:data_length] += stem.data[start:data_end] * effective_vol

        # マスターボリューム適用
        mixed *= self._master_volume

        # クリッピング防止
        return np.clip(mixed, -1.0, 1.0)

    def get_settings(self) -> Dict[str, Dict]:
        """現在の設定を辞書で取得"""
        return {
            "master_volume": self._master_volume,
            "stems": {
                name: {
                    "volume": stem.volume,
                    "muted": stem.muted,
                    "solo": stem.solo,
                }
                for name, stem in self._stems.items()
            },
        }

    def apply_settings(self, settings: Dict[str, Dict]) -> None:
        """設定を適用"""
        if "master_volume" in settings:
            self._master_volume = settings["master_volume"]

        if "stems" in settings:
            for name, stem_settings in settings["stems"].items():
                if name in self._stems:
                    self._stems[name].volume = stem_settings.get("volume", 1.0)
                    self._stems[name].muted = stem_settings.get("muted", False)
                    self._stems[name].solo = stem_settings.get("solo", False)

        self.mix_changed.emit()
