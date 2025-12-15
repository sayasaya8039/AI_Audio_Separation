"""
オーディオユーティリティ関数
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple

import numpy as np
import soundfile as sf


@dataclass
class AudioInfo:
    """オーディオファイル情報"""
    path: Path
    duration: float  # 秒
    sample_rate: int
    channels: int
    format: str
    subtype: str


def load_audio(
    file_path: str | Path,
    sample_rate: Optional[int] = None,
    mono: bool = False,
) -> Tuple[np.ndarray, int]:
    """
    オーディオファイルを読み込む

    Args:
        file_path: ファイルパス
        sample_rate: リサンプリングするサンプルレート（Noneの場合は元のまま）
        mono: Trueの場合モノラルに変換

    Returns:
        (audio_data, sample_rate) のタプル
        audio_data: shape (samples,) または (samples, channels)
    """
    file_path = Path(file_path)

    # soundfileで読み込み
    audio, sr = sf.read(str(file_path), dtype="float32")

    # モノラル変換
    if mono and audio.ndim > 1:
        audio = np.mean(audio, axis=1)

    # リサンプリング（必要な場合）
    if sample_rate is not None and sr != sample_rate:
        import librosa
        if audio.ndim == 1:
            audio = librosa.resample(audio, orig_sr=sr, target_sr=sample_rate)
        else:
            # ステレオの場合、各チャンネルをリサンプリング
            audio = np.stack([
                librosa.resample(audio[:, ch], orig_sr=sr, target_sr=sample_rate)
                for ch in range(audio.shape[1])
            ], axis=1)
        sr = sample_rate

    return audio, sr


def save_audio(
    file_path: str | Path,
    audio: np.ndarray,
    sample_rate: int,
    format: str = "WAV",
    subtype: str = "PCM_24",
) -> None:
    """
    オーディオファイルを保存する

    Args:
        file_path: 保存先パス
        audio: オーディオデータ
        sample_rate: サンプルレート
        format: ファイルフォーマット
        subtype: サブタイプ（ビット深度など）
    """
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    sf.write(str(file_path), audio, sample_rate, format=format, subtype=subtype)


def get_audio_info(file_path: str | Path) -> AudioInfo:
    """
    オーディオファイルの情報を取得

    Args:
        file_path: ファイルパス

    Returns:
        AudioInfo オブジェクト
    """
    file_path = Path(file_path)

    with sf.SoundFile(str(file_path)) as f:
        duration = len(f) / f.samplerate
        return AudioInfo(
            path=file_path,
            duration=duration,
            sample_rate=f.samplerate,
            channels=f.channels,
            format=f.format,
            subtype=f.subtype,
        )


def normalize_audio(audio: np.ndarray, target_db: float = -3.0) -> np.ndarray:
    """
    オーディオを正規化（ノーマライズ）

    Args:
        audio: オーディオデータ
        target_db: ターゲットdB（デフォルト: -3dB）

    Returns:
        正規化されたオーディオ
    """
    # 現在のピークを取得
    peak = np.max(np.abs(audio))
    if peak == 0:
        return audio

    # ターゲットレベルに正規化
    target_linear = 10 ** (target_db / 20)
    return audio * (target_linear / peak)


def mix_audio(
    audio_list: list[np.ndarray],
    volumes: Optional[list[float]] = None,
) -> np.ndarray:
    """
    複数のオーディオをミックス

    Args:
        audio_list: オーディオデータのリスト
        volumes: 各オーディオのボリューム（0.0〜1.0）

    Returns:
        ミックスされたオーディオ
    """
    if not audio_list:
        raise ValueError("オーディオリストが空です")

    if volumes is None:
        volumes = [1.0] * len(audio_list)

    # 最長のオーディオに合わせてパディング
    max_len = max(len(a) for a in audio_list)

    mixed = np.zeros(max_len, dtype=np.float32)
    for audio, vol in zip(audio_list, volumes):
        padded = np.pad(audio, (0, max_len - len(audio)), mode="constant")
        mixed += padded * vol

    # クリッピング防止
    return np.clip(mixed, -1.0, 1.0)


def format_time(seconds: float) -> str:
    """
    秒を MM:SS 形式にフォーマット

    Args:
        seconds: 秒数

    Returns:
        フォーマットされた時間文字列
    """
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02d}:{secs:02d}"
