"""
StemMixerのテスト
"""

import numpy as np
import pytest

from src.core.mixer import StemMixer, StemState


class TestStemState:
    """StemStateのテスト"""

    def test_default_values(self):
        """デフォルト値のテスト"""
        state = StemState(name="vocals")
        assert state.name == "vocals"
        assert state.volume == 1.0
        assert state.muted is False
        assert state.solo is False
        assert state.data is None

    def test_effective_volume_normal(self):
        """通常時の実効ボリューム"""
        state = StemState(name="vocals", volume=0.8)
        assert state.get_effective_volume(any_solo=False) == 0.8

    def test_effective_volume_muted(self):
        """ミュート時の実効ボリューム"""
        state = StemState(name="vocals", volume=0.8, muted=True)
        assert state.get_effective_volume(any_solo=False) == 0.0

    def test_effective_volume_solo_active_not_solo(self):
        """他がソロで自分がソロでない場合"""
        state = StemState(name="vocals", volume=0.8, solo=False)
        assert state.get_effective_volume(any_solo=True) == 0.0

    def test_effective_volume_solo_active_is_solo(self):
        """自分がソロの場合"""
        state = StemState(name="vocals", volume=0.8, solo=True)
        assert state.get_effective_volume(any_solo=True) == 0.8


class TestStemMixer:
    """StemMixerのテスト"""

    @pytest.fixture
    def mixer(self):
        """テスト用ミキサー"""
        return StemMixer()

    @pytest.fixture
    def sample_stems(self):
        """テスト用ステムデータ"""
        return {
            "vocals": np.random.randn(44100).astype(np.float32) * 0.5,
            "drums": np.random.randn(44100).astype(np.float32) * 0.5,
            "bass": np.random.randn(44100).astype(np.float32) * 0.5,
            "other": np.random.randn(44100).astype(np.float32) * 0.5,
        }

    def test_initial_state(self, mixer):
        """初期状態のテスト"""
        assert mixer.master_volume == 1.0
        for name in StemMixer.STEM_NAMES:
            assert mixer.get_volume(name) == 1.0
            assert mixer.is_muted(name) is False
            assert mixer.is_solo(name) is False

    def test_set_volume(self, mixer):
        """ボリューム設定のテスト"""
        mixer.set_volume("vocals", 0.5)
        assert mixer.get_volume("vocals") == 0.5

    def test_volume_clipping(self, mixer):
        """ボリュームのクリッピング"""
        mixer.set_volume("vocals", 1.5)
        assert mixer.get_volume("vocals") == 1.0

        mixer.set_volume("vocals", -0.5)
        assert mixer.get_volume("vocals") == 0.0

    def test_mute(self, mixer):
        """ミュートのテスト"""
        mixer.set_mute("drums", True)
        assert mixer.is_muted("drums") is True

        mixer.toggle_mute("drums")
        assert mixer.is_muted("drums") is False

    def test_solo(self, mixer):
        """ソロのテスト"""
        mixer.set_solo("bass", True)
        assert mixer.is_solo("bass") is True
        assert mixer.has_any_solo() is True

        mixer.clear_all_solo()
        assert mixer.is_solo("bass") is False
        assert mixer.has_any_solo() is False

    def test_load_stems(self, mixer, sample_stems):
        """ステム読み込みのテスト"""
        mixer.load_stems(sample_stems)

        for name in StemMixer.STEM_NAMES:
            stem = mixer.get_stem(name)
            assert stem is not None
            assert stem.data is not None
            assert len(stem.data) == 44100

    def test_get_mix(self, mixer, sample_stems):
        """ミックス取得のテスト"""
        mixer.load_stems(sample_stems)

        mix = mixer.get_mix()
        assert len(mix) == 44100
        assert mix.dtype == np.float32

    def test_get_mix_with_mute(self, mixer, sample_stems):
        """ミュート時のミックス"""
        mixer.load_stems(sample_stems)
        mixer.set_mute("vocals", True)
        mixer.set_mute("drums", True)
        mixer.set_mute("bass", True)
        mixer.set_mute("other", True)

        mix = mixer.get_mix()
        # 全ミュートなので無音
        assert np.allclose(mix, 0.0)

    def test_get_mix_with_solo(self, mixer, sample_stems):
        """ソロ時のミックス"""
        mixer.load_stems(sample_stems)
        mixer.set_solo("vocals", True)

        mix = mixer.get_mix()
        # vocalsのみが聞こえる
        expected = sample_stems["vocals"]
        assert np.allclose(mix, expected)

    def test_settings(self, mixer):
        """設定の保存・復元"""
        mixer.set_volume("vocals", 0.7)
        mixer.set_mute("drums", True)
        mixer.set_solo("bass", True)
        mixer.master_volume = 0.8

        settings = mixer.get_settings()

        # 新しいミキサーに復元
        new_mixer = StemMixer()
        new_mixer.apply_settings(settings)

        assert new_mixer.get_volume("vocals") == 0.7
        assert new_mixer.is_muted("drums") is True
        assert new_mixer.is_solo("bass") is True
        assert new_mixer.master_volume == 0.8


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
