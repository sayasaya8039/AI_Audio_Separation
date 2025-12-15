"""
ピッチ・テンポ変更エンジン

librosaを使用したピッチシフトとタイムストレッチ
"""

from typing import Optional

import numpy as np
from PyQt6.QtCore import QObject, QThread, pyqtSignal


class PitchTempoWorker(QThread):
    """バックグラウンドでピッチ/テンポ処理を行うワーカー"""

    progress = pyqtSignal(int, str)
    finished = pyqtSignal(np.ndarray)
    error = pyqtSignal(str)

    def __init__(
        self,
        audio: np.ndarray,
        sample_rate: int,
        pitch_shift: float = 0.0,
        tempo_ratio: float = 1.0,
        parent: Optional[QObject] = None,
    ):
        super().__init__(parent)
        self.audio = audio
        self.sample_rate = sample_rate
        self.pitch_shift = pitch_shift
        self.tempo_ratio = tempo_ratio
        self._cancelled = False

    def cancel(self) -> None:
        """処理をキャンセル"""
        self._cancelled = True

    def run(self) -> None:
        """処理を実行"""
        try:
            import librosa

            result = self.audio.copy()

            # テンポ変更（タイムストレッチ）
            if abs(self.tempo_ratio - 1.0) > 0.01:
                self.progress.emit(30, "テンポを変更中...")
                if self._cancelled:
                    return

                # pyrubberband が利用可能な場合は高品質処理
                try:
                    import pyrubberband as pyrb
                    result = pyrb.time_stretch(result, self.sample_rate, self.tempo_ratio)
                except ImportError:
                    # librosa のみで処理
                    result = librosa.effects.time_stretch(result, rate=self.tempo_ratio)

            # ピッチ変更
            if abs(self.pitch_shift) > 0.01:
                self.progress.emit(60, "ピッチを変更中...")
                if self._cancelled:
                    return

                try:
                    import pyrubberband as pyrb
                    result = pyrb.pitch_shift(result, self.sample_rate, self.pitch_shift)
                except ImportError:
                    result = librosa.effects.pitch_shift(
                        result, sr=self.sample_rate, n_steps=self.pitch_shift
                    )

            self.progress.emit(100, "完了")
            self.finished.emit(result.astype(np.float32))

        except Exception as e:
            self.error.emit(f"処理エラー: {str(e)}")


class PitchTempoProcessor(QObject):
    """
    ピッチ・テンポ変更プロセッサ

    使用例:
        processor = PitchTempoProcessor()
        processor.finished.connect(on_processed)
        processor.process(audio, sample_rate, pitch_shift=2, tempo_ratio=1.2)
    """

    progress = pyqtSignal(int, str)
    finished = pyqtSignal(np.ndarray)
    error = pyqtSignal(str)

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self._worker: Optional[PitchTempoWorker] = None

    def process(
        self,
        audio: np.ndarray,
        sample_rate: int,
        pitch_shift: float = 0.0,
        tempo_ratio: float = 1.0,
    ) -> None:
        """
        ピッチ/テンポ処理を開始

        Args:
            audio: オーディオデータ
            sample_rate: サンプルレート
            pitch_shift: ピッチシフト量（半音単位、-12〜+12）
            tempo_ratio: テンポ比率（0.5〜2.0）
        """
        # 既存のワーカーを停止
        if self._worker is not None and self._worker.isRunning():
            self._worker.cancel()
            self._worker.wait()

        # 新しいワーカーを作成
        self._worker = PitchTempoWorker(
            audio, sample_rate, pitch_shift, tempo_ratio, self
        )
        self._worker.progress.connect(self.progress.emit)
        self._worker.finished.connect(self.finished.emit)
        self._worker.error.connect(self.error.emit)
        self._worker.start()

    def process_sync(
        self,
        audio: np.ndarray,
        sample_rate: int,
        pitch_shift: float = 0.0,
        tempo_ratio: float = 1.0,
    ) -> np.ndarray:
        """
        同期的にピッチ/テンポ処理を実行

        Args:
            audio: オーディオデータ
            sample_rate: サンプルレート
            pitch_shift: ピッチシフト量（半音単位）
            tempo_ratio: テンポ比率

        Returns:
            処理されたオーディオデータ
        """
        import librosa

        result = audio.copy()

        # テンポ変更
        if abs(tempo_ratio - 1.0) > 0.01:
            try:
                import pyrubberband as pyrb
                result = pyrb.time_stretch(result, sample_rate, tempo_ratio)
            except ImportError:
                result = librosa.effects.time_stretch(result, rate=tempo_ratio)

        # ピッチ変更
        if abs(pitch_shift) > 0.01:
            try:
                import pyrubberband as pyrb
                result = pyrb.pitch_shift(result, sample_rate, pitch_shift)
            except ImportError:
                result = librosa.effects.pitch_shift(
                    result, sr=sample_rate, n_steps=pitch_shift
                )

        return result.astype(np.float32)

    def cancel(self) -> None:
        """処理をキャンセル"""
        if self._worker is not None:
            self._worker.cancel()

    def is_running(self) -> bool:
        """処理中かどうか"""
        return self._worker is not None and self._worker.isRunning()


def pitch_shift(
    audio: np.ndarray,
    sample_rate: int,
    semitones: float,
) -> np.ndarray:
    """
    ピッチを変更（便利関数）

    Args:
        audio: オーディオデータ
        sample_rate: サンプルレート
        semitones: 半音単位のシフト量（-12〜+12）

    Returns:
        ピッチシフトされたオーディオ
    """
    if abs(semitones) < 0.01:
        return audio

    try:
        import pyrubberband as pyrb
        return pyrb.pitch_shift(audio, sample_rate, semitones).astype(np.float32)
    except ImportError:
        import librosa
        return librosa.effects.pitch_shift(
            audio, sr=sample_rate, n_steps=semitones
        ).astype(np.float32)


def time_stretch(
    audio: np.ndarray,
    sample_rate: int,
    ratio: float,
) -> np.ndarray:
    """
    テンポを変更（便利関数）

    Args:
        audio: オーディオデータ
        sample_rate: サンプルレート
        ratio: 速度比率（0.5=半分の速度、2.0=2倍速）

    Returns:
        タイムストレッチされたオーディオ
    """
    if abs(ratio - 1.0) < 0.01:
        return audio

    try:
        import pyrubberband as pyrb
        return pyrb.time_stretch(audio, sample_rate, ratio).astype(np.float32)
    except ImportError:
        import librosa
        return librosa.effects.time_stretch(audio, rate=ratio).astype(np.float32)
