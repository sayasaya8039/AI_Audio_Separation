"""
オーディオエクスポーター

分離したステムやカスタムミックスをファイルに保存
"""

from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
import soundfile as sf
from PyQt6.QtCore import QObject, QThread, pyqtSignal

from src.core.mixer import StemMixer


class ExportWorker(QThread):
    """エクスポート処理を行うワーカー"""

    progress = pyqtSignal(int, str)
    finished = pyqtSignal(list)  # 保存したファイルパスのリスト
    error = pyqtSignal(str)

    def __init__(
        self,
        stems: Dict[str, np.ndarray],
        sample_rate: int,
        output_dir: Path,
        export_stems: bool = True,
        export_mix: bool = True,
        mix_volumes: Optional[Dict[str, float]] = None,
        format: str = "WAV",
        subtype: str = "PCM_24",
        parent: Optional[QObject] = None,
    ):
        super().__init__(parent)
        self.stems = stems
        self.sample_rate = sample_rate
        self.output_dir = output_dir
        self.export_stems = export_stems
        self.export_mix = export_mix
        self.mix_volumes = mix_volumes or {}
        self.format = format
        self.subtype = subtype
        self._cancelled = False

    def cancel(self) -> None:
        """処理をキャンセル"""
        self._cancelled = True

    def run(self) -> None:
        """エクスポート処理を実行"""
        try:
            saved_files: List[str] = []
            total_tasks = 0

            if self.export_stems:
                total_tasks += len(self.stems)
            if self.export_mix:
                total_tasks += 1

            current_task = 0

            # ステムを個別に保存
            if self.export_stems:
                for stem_name, stem_data in self.stems.items():
                    if self._cancelled:
                        return

                    progress = int((current_task / total_tasks) * 100)
                    self.progress.emit(progress, f"{stem_name}を保存中...")

                    file_path = self.output_dir / f"{stem_name}.wav"
                    sf.write(
                        str(file_path),
                        stem_data,
                        self.sample_rate,
                        format=self.format,
                        subtype=self.subtype,
                    )
                    saved_files.append(str(file_path))
                    current_task += 1

            # カスタムミックスを保存
            if self.export_mix:
                if self._cancelled:
                    return

                progress = int((current_task / total_tasks) * 100)
                self.progress.emit(progress, "ミックスを保存中...")

                # ミックスを作成
                max_len = max(len(s) for s in self.stems.values()) if self.stems else 0
                mixed = np.zeros(max_len, dtype=np.float32)

                for stem_name, stem_data in self.stems.items():
                    volume = self.mix_volumes.get(stem_name, 1.0)
                    if volume > 0:
                        padded = np.pad(
                            stem_data, (0, max_len - len(stem_data)), mode="constant"
                        )
                        mixed += padded * volume

                # クリッピング防止
                mixed = np.clip(mixed, -1.0, 1.0)

                file_path = self.output_dir / "mix.wav"
                sf.write(
                    str(file_path),
                    mixed,
                    self.sample_rate,
                    format=self.format,
                    subtype=self.subtype,
                )
                saved_files.append(str(file_path))

            self.progress.emit(100, "完了")
            self.finished.emit(saved_files)

        except Exception as e:
            self.error.emit(f"エクスポートエラー: {str(e)}")


class AudioExporter(QObject):
    """
    オーディオエクスポーター

    使用例:
        exporter = AudioExporter()
        exporter.finished.connect(on_exported)
        exporter.export_stems(stems, sample_rate, output_dir)
    """

    progress = pyqtSignal(int, str)
    finished = pyqtSignal(list)  # 保存したファイルパスのリスト
    error = pyqtSignal(str)

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self._worker: Optional[ExportWorker] = None

    def export_stems(
        self,
        stems: Dict[str, np.ndarray],
        sample_rate: int,
        output_dir: str | Path,
        format: str = "WAV",
        subtype: str = "PCM_24",
    ) -> None:
        """
        全ステムを個別ファイルとしてエクスポート

        Args:
            stems: ステム名 -> オーディオデータの辞書
            sample_rate: サンプルレート
            output_dir: 出力ディレクトリ
            format: ファイルフォーマット
            subtype: サブタイプ（ビット深度など）
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        self._start_worker(
            stems=stems,
            sample_rate=sample_rate,
            output_dir=output_dir,
            export_stems=True,
            export_mix=False,
            format=format,
            subtype=subtype,
        )

    def export_mix(
        self,
        stems: Dict[str, np.ndarray],
        sample_rate: int,
        output_path: str | Path,
        volumes: Optional[Dict[str, float]] = None,
        format: str = "WAV",
        subtype: str = "PCM_24",
    ) -> None:
        """
        カスタムミックスをエクスポート

        Args:
            stems: ステム名 -> オーディオデータの辞書
            sample_rate: サンプルレート
            output_path: 出力ファイルパス
            volumes: 各ステムのボリューム
            format: ファイルフォーマット
            subtype: サブタイプ
        """
        output_path = Path(output_path)
        output_dir = output_path.parent
        output_dir.mkdir(parents=True, exist_ok=True)

        self._start_worker(
            stems=stems,
            sample_rate=sample_rate,
            output_dir=output_dir,
            export_stems=False,
            export_mix=True,
            mix_volumes=volumes,
            format=format,
            subtype=subtype,
        )

    def export_all(
        self,
        stems: Dict[str, np.ndarray],
        sample_rate: int,
        output_dir: str | Path,
        volumes: Optional[Dict[str, float]] = None,
        format: str = "WAV",
        subtype: str = "PCM_24",
    ) -> None:
        """
        全ステムとカスタムミックスをエクスポート

        Args:
            stems: ステム名 -> オーディオデータの辞書
            sample_rate: サンプルレート
            output_dir: 出力ディレクトリ
            volumes: 各ステムのボリューム（ミックス用）
            format: ファイルフォーマット
            subtype: サブタイプ
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        self._start_worker(
            stems=stems,
            sample_rate=sample_rate,
            output_dir=output_dir,
            export_stems=True,
            export_mix=True,
            mix_volumes=volumes,
            format=format,
            subtype=subtype,
        )

    def _start_worker(
        self,
        stems: Dict[str, np.ndarray],
        sample_rate: int,
        output_dir: Path,
        export_stems: bool,
        export_mix: bool,
        mix_volumes: Optional[Dict[str, float]] = None,
        format: str = "WAV",
        subtype: str = "PCM_24",
    ) -> None:
        """ワーカーを開始"""
        # 既存のワーカーを停止
        if self._worker is not None and self._worker.isRunning():
            self._worker.cancel()
            self._worker.wait()

        # 新しいワーカーを作成
        self._worker = ExportWorker(
            stems=stems,
            sample_rate=sample_rate,
            output_dir=output_dir,
            export_stems=export_stems,
            export_mix=export_mix,
            mix_volumes=mix_volumes,
            format=format,
            subtype=subtype,
            parent=self,
        )
        self._worker.progress.connect(self.progress.emit)
        self._worker.finished.connect(self.finished.emit)
        self._worker.error.connect(self.error.emit)
        self._worker.start()

    def cancel(self) -> None:
        """処理をキャンセル"""
        if self._worker is not None:
            self._worker.cancel()

    def is_running(self) -> bool:
        """処理中かどうか"""
        return self._worker is not None and self._worker.isRunning()


def export_stem_sync(
    audio: np.ndarray,
    sample_rate: int,
    output_path: str | Path,
    format: str = "WAV",
    subtype: str = "PCM_24",
) -> None:
    """
    同期的にオーディオをエクスポート（便利関数）

    Args:
        audio: オーディオデータ
        sample_rate: サンプルレート
        output_path: 出力ファイルパス
        format: ファイルフォーマット
        subtype: サブタイプ
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    sf.write(str(output_path), audio, sample_rate, format=format, subtype=subtype)
