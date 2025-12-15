"""
メインアプリケーション

UIとコア機能を統合
"""

from pathlib import Path
from typing import Dict, Optional

import numpy as np
from PyQt6.QtCore import QObject
from PyQt6.QtWidgets import QFileDialog

from src.core.audio_player import AudioPlayer
from src.core.exporter import AudioExporter
from src.core.mixer import StemMixer
from src.core.pitch_tempo import PitchTempoProcessor
from src.core.separator import AudioSeparator, SeparationResult
from src.ui.main_window import MainWindow
from src.ui.theme import ThemeManager


class AudioSeparationApp(MainWindow):
    """
    AI Audio Separation アプリケーション

    UIとコア機能を統合したメインアプリケーションクラス
    """

    def __init__(self):
        super().__init__()

        # コアコンポーネント
        self._separator = AudioSeparator(self)
        self._player = AudioPlayer(self)
        self._mixer = StemMixer(self)
        self._pitch_tempo = PitchTempoProcessor(self)
        self._exporter = AudioExporter(self)

        # 状態
        self._current_file: Optional[Path] = None
        self._separation_result: Optional[SeparationResult] = None
        self._processed_stems: Dict[str, np.ndarray] = {}

        # 接続
        self._connect_signals()

        # テーマ適用
        ThemeManager().set_theme(ThemeManager().current_theme)

    def _connect_signals(self) -> None:
        """シグナルを接続"""
        # ファイル読み込み
        self.file_dropped.connect(self._load_file)
        self.file_selected.connect(self._load_file)

        # 分離
        self._separator.progress.connect(self._on_separation_progress)
        self._separator.finished.connect(self._on_separation_finished)
        self._separator.error.connect(self._on_error)

        # プレーヤー
        self._player.position_changed.connect(self._on_position_changed)
        self._player.state_changed.connect(self._on_playback_state_changed)
        self._player.playback_finished.connect(self._on_playback_finished)

        # トランスポートバー
        self.transport_bar.play_clicked.connect(self._player.play)
        self.transport_bar.pause_clicked.connect(self._player.pause)
        self.transport_bar.stop_clicked.connect(self._player.stop)
        self.transport_bar.seek_requested.connect(self._player.seek)
        self.transport_bar.skip_forward.connect(lambda: self._player.seek_relative(5))
        self.transport_bar.skip_backward.connect(lambda: self._player.seek_relative(-5))

        # ステムミキサー
        self.stem_mixer.volume_changed.connect(self._on_volume_changed)
        self.stem_mixer.mute_toggled.connect(self._on_mute_toggled)
        self.stem_mixer.solo_toggled.connect(self._on_solo_toggled)

        # ピッチ・テンポ
        self.pitch_tempo_control.pitch_changed.connect(self._on_pitch_changed)
        self.pitch_tempo_control.tempo_changed.connect(self._on_tempo_changed)

        # エクスポート
        self.export_requested.connect(self._export)
        self._exporter.progress.connect(self._on_export_progress)
        self._exporter.finished.connect(self._on_export_finished)
        self._exporter.error.connect(self._on_error)

    def _load_file(self, file_path: str) -> None:
        """ファイルを読み込んで分離"""
        self._current_file = Path(file_path)

        # 現在の再生を停止
        self._player.stop()

        # プログレス表示
        self.show_progress(True)
        self.set_progress(0, "分離処理を開始...")

        # 分離開始
        self._separator.separate(file_path)

        self.show_status(f"読み込み中: {self._current_file.name}")

    def _on_separation_progress(self, value: int, message: str) -> None:
        """分離進捗"""
        self.set_progress(value, message)

    def _on_separation_finished(self, result: SeparationResult) -> None:
        """分離完了"""
        self._separation_result = result

        # プログレス非表示
        self.show_progress(False)

        # ステムをプレーヤーとミキサーに読み込み
        stems = result.stems
        self._player.load_stems(stems, result.sample_rate)
        self._mixer.load_stems(stems)

        # 処理済みステムを初期化
        self._processed_stems = stems.copy()

        # 波形表示
        self.waveform_view.set_stems_overlay(stems, result.sample_rate)

        # UIを有効化
        self.set_loaded(True)
        self.transport_bar.set_duration(self._player.duration)

        # ステータス更新
        duration_str = self._format_time(self._player.duration)
        self.show_status(f"分離完了: {self._current_file.name} ({duration_str})")

    def _on_position_changed(self, position: float) -> None:
        """再生位置変更"""
        self.transport_bar.set_position(position)
        self.waveform_view.set_position(position)

    def _on_playback_state_changed(self, playing: bool) -> None:
        """再生状態変更"""
        self.transport_bar.set_playing(playing)

    def _on_playback_finished(self) -> None:
        """再生終了"""
        self.transport_bar.set_playing(False)

    def _on_volume_changed(self, stem: str, volume: float) -> None:
        """ステムボリューム変更"""
        self._player.set_volume(stem, volume)
        self._mixer.set_volume(stem, volume)

    def _on_mute_toggled(self, stem: str, muted: bool) -> None:
        """ステムミュート切り替え"""
        self._player.set_mute(stem, muted)
        self._mixer.set_mute(stem, muted)

    def _on_solo_toggled(self, stem: str, solo: bool) -> None:
        """ステムソロ切り替え"""
        self._player.set_solo(stem, solo)
        self._mixer.set_solo(stem, solo)

    def _on_pitch_changed(self, semitones: float) -> None:
        """ピッチ変更"""
        self._player.set_pitch(semitones)
        # リアルタイム処理は重いのでここでは反映しない
        # エクスポート時に適用

    def _on_tempo_changed(self, ratio: float) -> None:
        """テンポ変更"""
        self._player.set_tempo(ratio)
        # リアルタイム処理は重いのでここでは反映しない
        # エクスポート時に適用

    def _export(self) -> None:
        """エクスポートダイアログ"""
        if self._separation_result is None:
            return

        # 出力先を選択
        output_dir = QFileDialog.getExistingDirectory(
            self,
            "エクスポート先を選択",
            str(Path.home() / "Music"),
        )

        if not output_dir:
            return

        # 出力ディレクトリを作成
        if self._current_file:
            song_name = self._current_file.stem
            output_path = Path(output_dir) / song_name
        else:
            output_path = Path(output_dir) / "separated"

        output_path.mkdir(parents=True, exist_ok=True)

        # プログレス表示
        self.show_progress(True)
        self.set_progress(0, "エクスポート中...")

        # ピッチ/テンポが変更されている場合は処理
        pitch = self.pitch_tempo_control.pitch()
        tempo = self.pitch_tempo_control.tempo()

        stems_to_export = self._separation_result.stems

        if abs(pitch) > 0.01 or abs(tempo - 1.0) > 0.01:
            # ピッチ/テンポ処理
            processed = {}
            for name, audio in stems_to_export.items():
                processed[name] = self._pitch_tempo.process_sync(
                    audio,
                    self._separation_result.sample_rate,
                    pitch,
                    tempo,
                )
            stems_to_export = processed

        # エクスポート実行
        volumes = self.stem_mixer.get_volumes()
        self._exporter.export_all(
            stems=stems_to_export,
            sample_rate=self._separation_result.sample_rate,
            output_dir=output_path,
            volumes=volumes,
        )

    def _on_export_progress(self, value: int, message: str) -> None:
        """エクスポート進捗"""
        self.set_progress(value, message)

    def _on_export_finished(self, saved_files: list) -> None:
        """エクスポート完了"""
        self.show_progress(False)
        self.show_info(
            "エクスポート完了",
            f"{len(saved_files)}個のファイルを保存しました。",
        )
        self.show_status("エクスポート完了")

    def _on_error(self, message: str) -> None:
        """エラー処理"""
        self.show_progress(False)
        self.show_error("エラー", message)

    @staticmethod
    def _format_time(seconds: float) -> str:
        """時間をフォーマット"""
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"

    def closeEvent(self, event) -> None:
        """ウィンドウを閉じる前の処理"""
        # 再生を停止
        self._player.stop()

        # 分離処理をキャンセル
        if self._separator.is_running():
            self._separator.cancel()

        event.accept()
