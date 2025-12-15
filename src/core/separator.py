"""
Demucs音声分離エンジン

Hybrid Demucs v4を使用して音声を4ステムに分離:
- vocals: ボーカル
- drums: ドラム
- bass: ベース
- other: その他の楽器
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, Optional

import numpy as np
import torch
import torchaudio
from PyQt6.QtCore import QObject, QThread, pyqtSignal


@dataclass
class SeparationResult:
    """分離結果"""
    vocals: np.ndarray
    drums: np.ndarray
    bass: np.ndarray
    other: np.ndarray
    sample_rate: int
    original: np.ndarray

    def get_stem(self, name: str) -> np.ndarray:
        """ステム名からデータを取得"""
        stems = {
            "vocals": self.vocals,
            "drums": self.drums,
            "bass": self.bass,
            "other": self.other,
            "original": self.original,
        }
        return stems.get(name.lower(), self.original)

    @property
    def stems(self) -> Dict[str, np.ndarray]:
        """全ステムを辞書で取得"""
        return {
            "vocals": self.vocals,
            "drums": self.drums,
            "bass": self.bass,
            "other": self.other,
        }


class SeparationWorker(QThread):
    """バックグラウンドで音声分離を実行するワーカー"""

    # シグナル
    progress = pyqtSignal(int, str)  # (進捗%, メッセージ)
    finished = pyqtSignal(object)  # SeparationResult
    error = pyqtSignal(str)  # エラーメッセージ

    def __init__(
        self,
        file_path: str,
        device: Optional[str] = None,
        parent: Optional[QObject] = None,
    ):
        super().__init__(parent)
        self.file_path = file_path
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self._cancelled = False

    def cancel(self) -> None:
        """処理をキャンセル"""
        self._cancelled = True

    def run(self) -> None:
        """分離処理を実行"""
        try:
            self.progress.emit(0, "モデルを読み込み中...")

            # Demucsモデルを読み込み
            from demucs.pretrained import get_model
            from demucs.apply import apply_model

            model = get_model("htdemucs")
            model.to(self.device)
            model.eval()

            if self._cancelled:
                return

            self.progress.emit(20, "オーディオを読み込み中...")

            # オーディオを読み込み
            waveform, sample_rate = torchaudio.load(self.file_path)

            # ステレオに変換（必要な場合）
            if waveform.shape[0] == 1:
                waveform = waveform.repeat(2, 1)
            elif waveform.shape[0] > 2:
                waveform = waveform[:2]

            # モデルのサンプルレートにリサンプリング
            if sample_rate != model.samplerate:
                resampler = torchaudio.transforms.Resample(sample_rate, model.samplerate)
                waveform = resampler(waveform)
                sample_rate = model.samplerate

            if self._cancelled:
                return

            self.progress.emit(40, "音声を分離中...")

            # バッチ次元を追加
            waveform = waveform.unsqueeze(0).to(self.device)

            # 分離実行
            with torch.no_grad():
                sources = apply_model(model, waveform, device=self.device, progress=True)

            if self._cancelled:
                return

            self.progress.emit(80, "結果を処理中...")

            # 結果を取り出し（CPU、NumPy配列に変換）
            sources = sources.squeeze(0).cpu().numpy()

            # Demucsの出力順序: drums, bass, other, vocals
            # モデルによって異なる場合があるので確認
            source_names = model.sources
            stem_dict = {}
            for i, name in enumerate(source_names):
                # ステレオからモノラルに変換（平均）
                stem_dict[name] = np.mean(sources[i], axis=0).astype(np.float32)

            # オリジナルもモノラルに
            original = np.mean(waveform.squeeze(0).cpu().numpy(), axis=0).astype(np.float32)

            self.progress.emit(100, "完了")

            result = SeparationResult(
                vocals=stem_dict.get("vocals", np.zeros_like(original)),
                drums=stem_dict.get("drums", np.zeros_like(original)),
                bass=stem_dict.get("bass", np.zeros_like(original)),
                other=stem_dict.get("other", np.zeros_like(original)),
                sample_rate=sample_rate,
                original=original,
            )

            self.finished.emit(result)

        except Exception as e:
            self.error.emit(f"分離エラー: {str(e)}")


class AudioSeparator(QObject):
    """
    音声分離エンジン

    使用例:
        separator = AudioSeparator()
        separator.progress.connect(on_progress)
        separator.finished.connect(on_finished)
        separator.separate("song.mp3")
    """

    # シグナル
    progress = pyqtSignal(int, str)
    finished = pyqtSignal(object)  # SeparationResult
    error = pyqtSignal(str)

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self._worker: Optional[SeparationWorker] = None
        self._device = "cuda" if torch.cuda.is_available() else "cpu"
        self._result: Optional[SeparationResult] = None

    @property
    def device(self) -> str:
        """使用中のデバイス"""
        return self._device

    @property
    def is_gpu_available(self) -> bool:
        """GPUが利用可能か"""
        return torch.cuda.is_available()

    @property
    def result(self) -> Optional[SeparationResult]:
        """最後の分離結果"""
        return self._result

    def separate(self, file_path: str | Path) -> None:
        """
        音声ファイルを分離

        Args:
            file_path: 音声ファイルのパス
        """
        # 既存のワーカーがあれば停止
        if self._worker is not None and self._worker.isRunning():
            self._worker.cancel()
            self._worker.wait()

        # 新しいワーカーを作成
        self._worker = SeparationWorker(str(file_path), self._device, self)
        self._worker.progress.connect(self.progress.emit)
        self._worker.finished.connect(self._on_finished)
        self._worker.error.connect(self.error.emit)
        self._worker.start()

    def cancel(self) -> None:
        """分離処理をキャンセル"""
        if self._worker is not None:
            self._worker.cancel()

    def is_running(self) -> bool:
        """処理中かどうか"""
        return self._worker is not None and self._worker.isRunning()

    def _on_finished(self, result: SeparationResult) -> None:
        """分離完了時のコールバック"""
        self._result = result
        self.finished.emit(result)
