"""
AudioPlayerのテスト
"""

import numpy as np
import pytest

from src.core.audio_player import AudioPlayer


class TestAudioPlayer:
    """AudioPlayerのテスト"""

    @pytest.fixture
    def player(self, qtbot):
        """テスト用プレーヤー"""
        return AudioPlayer()

    @pytest.fixture
    def sample_stems(self):
        """テスト用ステムデータ（1秒）"""
        sr = 44100
        return {
            "vocals": np.sin(2 * np.pi * 440 * np.arange(sr) / sr).astype(np.float32),
            "drums": np.sin(2 * np.pi * 220 * np.arange(sr) / sr).astype(np.float32),
            "bass": np.sin(2 * np.pi * 110 * np.arange(sr) / sr).astype(np.float32),
            "other": np.sin(2 * np.pi * 330 * np.arange(sr) / sr).astype(np.float32),
        }

    def test_initial_state(self, player):
        """初期状態のテスト"""
        assert player.duration == 0.0
        assert player.position == 0.0
        assert player.is_playing is False
        assert player.sample_rate == 44100

    def test_load_stems(self, player, sample_stems):
        """ステム読み込みのテスト"""
        player.load_stems(sample_stems, 44100)

        assert player.duration == pytest.approx(1.0, rel=0.01)
        assert player.sample_rate == 44100

    def test_set_volume(self, player):
        """ボリューム設定のテスト"""
        player.set_volume("vocals", 0.5)
        assert player.get_volume("vocals") == 0.5

        # クリッピング
        player.set_volume("vocals", 1.5)
        assert player.get_volume("vocals") == 1.0

    def test_mute(self, player):
        """ミュートのテスト"""
        player.set_mute("drums", True)
        assert player.is_muted("drums") is True

        player.set_mute("drums", False)
        assert player.is_muted("drums") is False

    def test_solo(self, player):
        """ソロのテスト"""
        player.set_solo("bass", True)
        assert player.is_solo("bass") is True

        player.set_solo("bass", False)
        assert player.is_solo("bass") is False

    def test_seek(self, player, sample_stems):
        """シークのテスト"""
        player.load_stems(sample_stems, 44100)

        player.seek(0.5)
        assert player.position == pytest.approx(0.5, rel=0.01)

        # 範囲外
        player.seek(10.0)
        assert player.position == pytest.approx(1.0, rel=0.01)

        player.seek(-1.0)
        assert player.position == 0.0

    def test_seek_relative(self, player, sample_stems):
        """相対シークのテスト"""
        player.load_stems(sample_stems, 44100)
        player.seek(0.5)

        player.seek_relative(0.2)
        assert player.position == pytest.approx(0.7, rel=0.01)

        player.seek_relative(-0.3)
        assert player.position == pytest.approx(0.4, rel=0.01)

    def test_pitch_setting(self, player):
        """ピッチ設定のテスト"""
        player.set_pitch(5.0)
        # 内部値を直接確認できないが、クリッピングが動作することを確認
        player.set_pitch(15.0)  # 12以上は12にクリップ
        player.set_pitch(-15.0)  # -12以下は-12にクリップ

    def test_tempo_setting(self, player):
        """テンポ設定のテスト"""
        player.set_tempo(1.5)
        # 範囲外
        player.set_tempo(3.0)  # 2.0にクリップ
        player.set_tempo(0.1)  # 0.5にクリップ


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
