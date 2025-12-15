"""
リアルタイムオーディオプレーヤー

sounddeviceを使用した低遅延オーディオ再生
"""

from typing import Callable, Dict, List, Optional

import numpy as np
import sounddevice as sd
from PyQt6.QtCore import QObject, QTimer, pyqtSignal


class AudioPlayer(QObject):
    """
    リアルタイムオーディオプレーヤー

    複数のステムを個別のボリュームでミックスしながら再生
    """

    # シグナル
    position_changed = pyqtSignal(float)  # 現在位置（秒）
    playback_finished = pyqtSignal()
    state_changed = pyqtSignal(bool)  # True=再生中, False=停止

    # 定数
    BUFFER_SIZE = 2048
    UPDATE_INTERVAL = 50  # ms

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)

        # オーディオデータ
        self._stems: Dict[str, np.ndarray] = {}
        self._sample_rate: int = 44100
        self._duration: float = 0.0

        # ミキシング設定
        self._volumes: Dict[str, float] = {
            "vocals": 1.0,
            "drums": 1.0,
            "bass": 1.0,
            "other": 1.0,
        }
        self._mutes: Dict[str, bool] = {
            "vocals": False,
            "drums": False,
            "bass": False,
            "other": False,
        }
        self._solos: Dict[str, bool] = {
            "vocals": False,
            "drums": False,
            "bass": False,
            "other": False,
        }
        self._master_volume: float = 1.0

        # ピッチ・テンポ
        self._pitch_shift: float = 0.0  # 半音単位
        self._tempo_ratio: float = 1.0  # 1.0 = 100%

        # 再生状態
        self._position: int = 0  # サンプル位置
        self._is_playing: bool = False
        self._stream: Optional[sd.OutputStream] = None

        # 位置更新タイマー
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update_position)

    @property
    def duration(self) -> float:
        """総再生時間（秒）"""
        return self._duration

    @property
    def position(self) -> float:
        """現在位置（秒）"""
        return self._position / self._sample_rate if self._sample_rate > 0 else 0.0

    @property
    def is_playing(self) -> bool:
        """再生中かどうか"""
        return self._is_playing

    @property
    def sample_rate(self) -> int:
        """サンプルレート"""
        return self._sample_rate

    def load_stems(
        self,
        stems: Dict[str, np.ndarray],
        sample_rate: int,
    ) -> None:
        """
        ステムデータを読み込み

        Args:
            stems: ステム名 -> オーディオデータの辞書
            sample_rate: サンプルレート
        """
        self.stop()

        self._stems = stems
        self._sample_rate = sample_rate
        self._position = 0

        # 最長のステムから総時間を計算
        if stems:
            max_samples = max(len(s) for s in stems.values())
            self._duration = max_samples / sample_rate
        else:
            self._duration = 0.0

    def set_volume(self, stem: str, volume: float) -> None:
        """
        ステムのボリュームを設定

        Args:
            stem: ステム名
            volume: ボリューム（0.0〜1.0）
        """
        if stem in self._volumes:
            self._volumes[stem] = np.clip(volume, 0.0, 1.0)

    def get_volume(self, stem: str) -> float:
        """ステムのボリュームを取得"""
        return self._volumes.get(stem, 1.0)

    def set_mute(self, stem: str, muted: bool) -> None:
        """ステムのミュートを設定"""
        if stem in self._mutes:
            self._mutes[stem] = muted

    def is_muted(self, stem: str) -> bool:
        """ステムがミュートされているか"""
        return self._mutes.get(stem, False)

    def set_solo(self, stem: str, solo: bool) -> None:
        """ステムのソロを設定"""
        if stem in self._solos:
            self._solos[stem] = solo

    def is_solo(self, stem: str) -> bool:
        """ステムがソロかどうか"""
        return self._solos.get(stem, False)

    def set_master_volume(self, volume: float) -> None:
        """マスターボリュームを設定"""
        self._master_volume = np.clip(volume, 0.0, 1.0)

    def set_pitch(self, semitones: float) -> None:
        """ピッチシフトを設定（半音単位）"""
        self._pitch_shift = np.clip(semitones, -12.0, 12.0)

    def set_tempo(self, ratio: float) -> None:
        """テンポ比率を設定（0.5〜2.0）"""
        self._tempo_ratio = np.clip(ratio, 0.5, 2.0)

    def play(self) -> None:
        """再生開始"""
        if not self._stems:
            return

        if self._is_playing:
            return

        self._is_playing = True

        # オーディオストリームを開始
        self._stream = sd.OutputStream(
            samplerate=self._sample_rate,
            channels=1,
            dtype="float32",
            blocksize=self.BUFFER_SIZE,
            callback=self._audio_callback,
        )
        self._stream.start()

        # タイマー開始
        self._timer.start(self.UPDATE_INTERVAL)

        self.state_changed.emit(True)

    def pause(self) -> None:
        """一時停止"""
        if not self._is_playing:
            return

        self._is_playing = False

        # ストリームを停止
        if self._stream is not None:
            self._stream.stop()
            self._stream.close()
            self._stream = None

        # タイマー停止
        self._timer.stop()

        self.state_changed.emit(False)

    def stop(self) -> None:
        """停止（位置をリセット）"""
        self.pause()
        self._position = 0
        self.position_changed.emit(0.0)

    def toggle_playback(self) -> None:
        """再生/一時停止を切り替え"""
        if self._is_playing:
            self.pause()
        else:
            self.play()

    def seek(self, seconds: float) -> None:
        """
        指定位置にシーク

        Args:
            seconds: シーク先の位置（秒）
        """
        seconds = np.clip(seconds, 0.0, self._duration)
        self._position = int(seconds * self._sample_rate)
        self.position_changed.emit(seconds)

    def seek_relative(self, delta_seconds: float) -> None:
        """相対シーク"""
        self.seek(self.position + delta_seconds)

    def _audio_callback(
        self,
        outdata: np.ndarray,
        frames: int,
        time_info: dict,
        status: sd.CallbackFlags,
    ) -> None:
        """オーディオコールバック（バッファ書き込み）"""
        if not self._is_playing:
            outdata.fill(0)
            return

        # ミックスバッファを作成
        mixed = np.zeros(frames, dtype=np.float32)

        # ソロがあるか確認
        any_solo = any(self._solos.values())

        # 各ステムをミックス
        for stem_name, stem_data in self._stems.items():
            # ソロ/ミュートチェック
            if any_solo and not self._solos.get(stem_name, False):
                continue
            if self._mutes.get(stem_name, False):
                continue

            # ボリューム取得
            volume = self._volumes.get(stem_name, 1.0)
            if volume <= 0:
                continue

            # データ範囲を取得
            start = self._position
            end = min(start + frames, len(stem_data))
            actual_frames = end - start

            if actual_frames <= 0:
                continue

            # ミックスに加算
            mixed[:actual_frames] += stem_data[start:end] * volume

        # マスターボリュームを適用
        mixed *= self._master_volume

        # クリッピング防止
        mixed = np.clip(mixed, -1.0, 1.0)

        # 出力バッファに書き込み
        outdata[:, 0] = mixed

        # 位置を進める
        self._position += frames

        # 終端チェック
        max_len = max((len(s) for s in self._stems.values()), default=0)
        if self._position >= max_len:
            self._position = 0
            # 再生終了は別スレッドなのでコールバックでは直接呼ばない

    def _update_position(self) -> None:
        """位置更新（タイマーから呼ばれる）"""
        if self._is_playing:
            self.position_changed.emit(self.position)

            # 終端チェック
            max_len = max((len(s) for s in self._stems.values()), default=0)
            if self._position >= max_len:
                self.stop()
                self.playback_finished.emit()
