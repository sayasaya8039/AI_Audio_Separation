"""
ファイル操作ユーティリティ
"""

from pathlib import Path
from typing import Set


# サポートするオーディオフォーマット
SUPPORTED_FORMATS: Set[str] = {
    ".mp3",
    ".wav",
    ".flac",
    ".m4a",
    ".aac",
    ".ogg",
    ".wma",
    ".aiff",
}


def get_supported_formats() -> Set[str]:
    """
    サポートするファイル形式を取得

    Returns:
        サポートする拡張子のセット
    """
    return SUPPORTED_FORMATS.copy()


def is_supported_format(file_path: str | Path) -> bool:
    """
    ファイルがサポートされている形式かチェック

    Args:
        file_path: ファイルパス

    Returns:
        サポートされていればTrue
    """
    path = Path(file_path)
    return path.suffix.lower() in SUPPORTED_FORMATS


def get_file_filter() -> str:
    """
    ファイルダイアログ用のフィルタ文字列を取得

    Returns:
        フィルタ文字列（例: "Audio Files (*.mp3 *.wav ...)"）
    """
    extensions = " ".join(f"*{ext}" for ext in sorted(SUPPORTED_FORMATS))
    return f"音声ファイル ({extensions})"


def ensure_directory(path: str | Path) -> Path:
    """
    ディレクトリが存在することを保証

    Args:
        path: ディレクトリパス

    Returns:
        作成/確認されたディレクトリのPath
    """
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_unique_filename(directory: str | Path, base_name: str, extension: str) -> Path:
    """
    重複しないファイル名を生成

    Args:
        directory: ディレクトリパス
        base_name: ベースファイル名
        extension: 拡張子（.を含む）

    Returns:
        重複しないファイルパス
    """
    directory = Path(directory)
    counter = 0
    while True:
        if counter == 0:
            file_name = f"{base_name}{extension}"
        else:
            file_name = f"{base_name}_{counter}{extension}"

        file_path = directory / file_name
        if not file_path.exists():
            return file_path
        counter += 1


def get_output_directory(base_dir: str | Path, song_name: str) -> Path:
    """
    出力用ディレクトリを取得/作成

    Args:
        base_dir: ベースディレクトリ
        song_name: 曲名

    Returns:
        出力ディレクトリのPath
    """
    # ファイル名に使えない文字を除去
    safe_name = "".join(c for c in song_name if c not in r'<>:"/\|?*')
    output_dir = Path(base_dir) / safe_name
    return ensure_directory(output_dir)
