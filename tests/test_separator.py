"""
AudioSeparatorのテスト

注: 実際の分離処理はDemucsモデルが必要なため、
ユニットテストでは構造のテストのみ行う
"""

import numpy as np
import pytest

from src.core.separator import SeparationResult


class TestSeparationResult:
    """SeparationResultのテスト"""

    @pytest.fixture
    def sample_result(self):
        """テスト用の分離結果"""
        sr = 44100
        length = sr  # 1秒

        return SeparationResult(
            vocals=np.random.randn(length).astype(np.float32),
            drums=np.random.randn(length).astype(np.float32),
            bass=np.random.randn(length).astype(np.float32),
            other=np.random.randn(length).astype(np.float32),
            sample_rate=sr,
            original=np.random.randn(length).astype(np.float32),
        )

    def test_get_stem(self, sample_result):
        """ステム取得のテスト"""
        vocals = sample_result.get_stem("vocals")
        assert vocals is not None
        assert len(vocals) == 44100

        drums = sample_result.get_stem("drums")
        assert drums is not None

        # 存在しないステムはoriginalを返す
        unknown = sample_result.get_stem("unknown")
        assert np.array_equal(unknown, sample_result.original)

    def test_stems_property(self, sample_result):
        """stemsプロパティのテスト"""
        stems = sample_result.stems

        assert "vocals" in stems
        assert "drums" in stems
        assert "bass" in stems
        assert "other" in stems
        assert "original" not in stems  # originalは含まれない

    def test_sample_rate(self, sample_result):
        """サンプルレートのテスト"""
        assert sample_result.sample_rate == 44100


class TestAudioSeparator:
    """AudioSeparatorのテスト（モックなし）"""

    def test_import(self):
        """インポートのテスト"""
        from src.core.separator import AudioSeparator
        assert AudioSeparator is not None

    def test_device_property(self):
        """デバイスプロパティのテスト"""
        from src.core.separator import AudioSeparator

        separator = AudioSeparator()
        device = separator.device
        assert device in ["cuda", "cpu"]

    def test_is_running_initial(self):
        """初期状態でis_runningはFalse"""
        from src.core.separator import AudioSeparator

        separator = AudioSeparator()
        assert separator.is_running() is False

    def test_result_initial(self):
        """初期状態でresultはNone"""
        from src.core.separator import AudioSeparator

        separator = AudioSeparator()
        assert separator.result is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
