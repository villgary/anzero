"""
Unit tests for D-25 Confidence Fusion Engine.

Tests the FusionEngine and LightGBMModel implementations.
"""

import pytest
import numpy as np
from app.detection_engine.d25.fusion_engine import FusionEngine, ConfidenceResult
from app.detection_engine.d25.lightgbm_model import LightGBMModel


@pytest.fixture
def engine():
    return FusionEngine()


@pytest.fixture
def lightgbm_model():
    return LightGBMModel()


class TestFusionEngine:
    """Test cases for FusionEngine class."""

    def test_fusion_35_dimensions(self, engine):
        """Test that fusion engine handles 35-dimensional input."""
        signals = np.random.rand(35).tolist()
        context = {
            "hour_of_day": 14,
            "day_of_week": 1,
            "source_ip_count": 3,
            "asset_type": "web"
        }
        result = engine.score(signals, context)

        assert 0.0 <= result.score <= 1.0
        assert result.level in ["observe", "investigate", "respond", "emergency"]
        assert isinstance(result.breakdown, dict)
        assert isinstance(result.explanation, str)

    def test_weights_sum_to_one(self, engine):
        """Test that softmax-normalized weights sum to 1.0."""
        weights_sum = np.sum(engine.weights)
        assert abs(weights_sum - 1.0) < 1e-6

    def test_context_normalization(self, engine):
        """Test context feature normalization."""
        context = {
            "hour_of_day": 12,
            "day_of_week": 3,
            "source_ip_count": 5,
            "asset_type": "api"
        }
        normalized = engine._normalize_context(context)

        assert len(normalized) == 6
        assert 0.0 <= normalized[0] <= 1.0  # hour_of_day
        assert 0.0 <= normalized[1] <= 1.0  # day_of_week
        assert 0.0 <= normalized[2] <= 1.0  # source_ip_count
        assert normalized[3] == 0.0  # asset_type_web
        assert normalized[4] == 1.0  # asset_type_api
        assert normalized[5] == 0.0  # asset_type_db

    def test_context_defaults(self, engine):
        """Test default values when context is incomplete."""
        context = {}
        normalized = engine._normalize_context(context)

        assert len(normalized) == 6
        assert normalized[0] == 12 / 24.0  # default hour
        assert normalized[1] == 0 / 7.0    # default day
        assert normalized[2] == 1 / 10.0   # default source_ip_count

    def test_level_mapping_observe(self, engine):
        """Test observe level threshold (0.0 - 0.30)."""
        assert engine._map_to_level(0.0) == "observe"
        assert engine._map_to_level(0.15) == "observe"
        assert engine._map_to_level(0.29) == "observe"

    def test_level_mapping_investigate(self, engine):
        """Test investigate level threshold (0.30 - 0.59)."""
        assert engine._map_to_level(0.30) == "investigate"
        assert engine._map_to_level(0.45) == "investigate"
        assert engine._map_to_level(0.59) == "investigate"

    def test_level_mapping_respond(self, engine):
        """Test respond level threshold (0.60 - 0.84)."""
        assert engine._map_to_level(0.60) == "respond"
        assert engine._map_to_level(0.70) == "respond"
        assert engine._map_to_level(0.84) == "respond"

    def test_level_mapping_emergency(self, engine):
        """Test emergency level threshold (0.85 - 1.00)."""
        assert engine._map_to_level(0.85) == "emergency"
        assert engine._map_to_level(0.92) == "emergency"
        assert engine._map_to_level(1.0) == "emergency"

    def test_platt_scaling(self, engine):
        """Test Platt scaling calibration."""
        # Raw scores should be transformed to calibrated probabilities
        raw_scores = [-1.0, 0.0, 1.0]
        for raw in raw_scores:
            calibrated = engine._platt_scaling(raw)
            assert 0.0 <= calibrated <= 1.0

    def test_score_clamping(self, engine):
        """Test that scores are clamped to [0.0, 1.0] range."""
        assert engine._clamp_score(-0.5) == 0.0
        assert engine._clamp_score(0.5) == 0.5
        assert engine._clamp_score(1.5) == 1.0

    def test_layer_weights_defined(self, engine):
        """Test that layer weights are correctly defined."""
        expected_weights = {"L1": 0.15, "L2": 0.25, "L3": 0.15, "L4": 0.20, "L5": 0.15}
        assert engine.LAYER_WEIGHTS == expected_weights

    def test_layer_signals_mapping(self, engine):
        """Test that layer-to-signal mapping is correct."""
        # L1: signals 0-5 (6 signals)
        assert engine.LAYER_SIGNALS["L1"] == list(range(0, 6))
        # L2: signals 6-11 (6 signals)
        assert engine.LAYER_SIGNALS["L2"] == list(range(6, 12))
        # L3: signals 12-14 (3 signals)
        assert engine.LAYER_SIGNALS["L3"] == list(range(12, 15))
        # L4: signals 15-20 (6 signals)
        assert engine.LAYER_SIGNALS["L4"] == list(range(15, 21))
        # L5: signals 21-28 (8 signals)
        assert engine.LAYER_SIGNALS["L5"] == list(range(21, 29))

    def test_high_signal_input(self, engine):
        """Test with high-value detection signals."""
        signals = [0.9] * 29 + [1.0] * 6
        context = {"asset_type": "web"}
        result = engine.score(signals, context)

        # High signals should result in high confidence
        assert result.score > 0.3
        assert result.level in ["investigate", "respond", "emergency"]

    def test_low_signal_input(self, engine):
        """Test with low-value detection signals."""
        signals = [0.05] * 29 + [0.0] * 6
        context = {"asset_type": "db"}
        result = engine.score(signals, context)

        # Low signals should result in low confidence
        assert result.score < 0.5
        assert result.level in ["observe", "investigate"]

    def test_confidence_result_dataclass(self):
        """Test ConfidenceResult dataclass creation."""
        result = ConfidenceResult(
            score=0.75,
            level="respond",
            breakdown={"test": "data"},
            explanation="Test explanation"
        )

        assert result.score == 0.75
        assert result.level == "respond"
        assert result.breakdown == {"test": "data"}
        assert result.explanation == "Test explanation"

    def test_explanation_contains_signal_info(self, engine):
        """Test that explanation contains signal information."""
        signals = [0.1] * 29 + [0.0] * 6
        context = {"asset_type": "web"}
        result = engine.score(signals, context)

        assert "置信度" in result.explanation
        assert "风险等级" in result.explanation
        assert "资产类型" in result.explanation


class TestLightGBMModel:
    """Test cases for LightGBMModel class."""

    def test_model_initialization(self, lightgbm_model):
        """Test model initialization."""
        assert lightgbm_model.n_features == 35
        assert lightgbm_model.model is not None

    def test_predict_single_sample(self, lightgbm_model):
        """Test prediction with single sample."""
        features = np.random.rand(35)
        prediction = lightgbm_model.predict(features)

        assert isinstance(prediction, np.ndarray)
        assert prediction.shape == (1,)

    def test_predict_multiple_samples(self, lightgbm_model):
        """Test prediction with multiple samples."""
        features = np.random.rand(10, 35)
        predictions = lightgbm_model.predict(features)

        assert predictions.shape == (10,)

    def test_predict_proba(self, lightgbm_model):
        """Test probability prediction."""
        features = np.random.rand(5, 35)
        proba = lightgbm_model.predict_proba(features)

        assert proba.shape == (5, 2)
        assert np.allclose(proba[:, 0] + proba[:, 1], 1.0)

    def test_predict_with_list_input(self, lightgbm_model):
        """Test prediction with list input."""
        features = np.random.rand(35).tolist()
        prediction = lightgbm_model.predict(features)

        assert isinstance(prediction, np.ndarray)
        assert prediction.shape == (1,)

    def test_mock_model_weights(self, lightgbm_model):
        """Test that mock model weights sum to 1."""
        if hasattr(lightgbm_model.model, 'weights'):
            assert abs(lightgbm_model.model.weights.sum() - 1.0) < 1e-6

    def test_feature_importance(self, lightgbm_model):
        """Test feature importance retrieval."""
        importance = lightgbm_model.get_feature_importance()

        assert importance.shape == (35,)
        assert np.all(importance >= 0)
