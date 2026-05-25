import numpy as np
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class ConfidenceResult:
    score: float
    level: str
    breakdown: dict
    explanation: str


class FusionEngine:
    """
    D-25 Multi-Signal Fusion Confidence Engine

    Implements weighted fusion of detection signals from L1-L5 layers
    with context-aware calibration and Platt scaling.

    Input: 35-dimensional feature vector
    - 29 detection signals (D-01 to D-29)
    - 6 context features (normalized)

    Layer weights: L1=0.15, L2=0.25, L3=0.15, L4=0.20, L5=0.15
    """
    LAYER_WEIGHTS = {
        "L1": 0.15, "L2": 0.25, "L3": 0.15, "L4": 0.20, "L5": 0.15
    }

    # Detection signal indices by layer
    LAYER_SIGNALS = {
        "L1": list(range(0, 6)),      # D-01 to D-06 (6 signals)
        "L2": list(range(6, 12)),     # D-07 to D-12 (6 signals)
        "L3": list(range(12, 15)),    # D-13 to D-15 (3 signals)
        "L4": list(range(15, 21)),    # D-16 to D-21 (6 signals)
        "L5": list(range(21, 29)),    # D-22 to D-29 (8 signals)
    }

    # Context feature indices (appended after 29 detection signals)
    CONTEXT_FEATURES = {
        "hour_of_day": 29,
        "day_of_week": 30,
        "source_ip_count": 31,
        "asset_type_web": 32,
        "asset_type_api": 33,
        "asset_type_db": 34,
    }

    # Level thresholds for threat response levels
    THRESHOLD_OBSERVE = 0.30
    THRESHOLD_INVESTIGATE = 0.60
    THRESHOLD_RESPOND = 0.85

    # Platt scaling parameters (calibrated for detection task)
    PLATT_A = 1.5
    PLATT_B = -0.5

    def __init__(self):
        self.weights = self._build_layer_weights()

    def _build_layer_weights(self) -> np.ndarray:
        """
        Build 35-dimensional weight vector with layer-based weights.
        Uses softmax normalization to ensure weights sum to 1.0.
        """
        # Initialize 35-dim weight array
        weights = np.zeros(35)

        # Assign layer weights to detection signals
        for layer, indices in self.LAYER_SIGNALS.items():
            layer_weight = self.LAYER_WEIGHTS[layer]
            for idx in indices:
                weights[idx] = layer_weight

        # Context features get uniform weight (distributed from L4 allocation)
        context_weight = 0.05  # Small weight for context
        for idx in self.CONTEXT_FEATURES.values():
            weights[idx] = context_weight

        # Apply softmax normalization
        weights = self._softmax(weights)
        return weights

    def _softmax(self, x: np.ndarray) -> np.ndarray:
        """Apply softmax normalization to ensure weights sum to 1.0."""
        exp_x = np.exp(x - np.max(x))  # Subtract max for numerical stability
        return exp_x / np.sum(exp_x)

    def _platt_scaling(self, raw_score: float) -> float:
        """
        Apply Platt scaling calibration.
        Maps raw weighted score to calibrated probability [0, 1].
        """
        # Sigmoid transformation with parameters tuned for detection
        calibrated = 1.0 / (1.0 + np.exp(-(self.PLATT_A * raw_score + self.PLATT_B)))
        return self._clamp_score(calibrated)

    def _clamp_score(self, raw: float) -> float:
        """Clamp score to [0.0, 1.0] range."""
        return min(1.0, max(0.0, raw))

    def _normalize_context(self, context: dict) -> np.ndarray:
        """
        Normalize context features to [0, 1] range.
        Returns 6-dimensional context vector.
        """
        # Default values if context is incomplete
        hour_of_day = context.get("hour_of_day", 12) / 24.0
        day_of_week = context.get("day_of_week", 0) / 7.0
        source_ip_count = context.get("source_ip_count", 1) / 10.0

        asset_type = context.get("asset_type", "web")
        asset_type_web = 1.0 if asset_type == "web" else 0.0
        asset_type_api = 1.0 if asset_type == "api" else 0.0
        asset_type_db = 1.0 if asset_type == "db" else 0.0

        return np.array([
            hour_of_day,
            day_of_week,
            source_ip_count,
            asset_type_web,
            asset_type_api,
            asset_type_db,
        ])

    def _map_to_level(self, score: float) -> str:
        """Map confidence score to threat response level."""
        if score < self.THRESHOLD_OBSERVE:
            return "observe"
        elif score < self.THRESHOLD_INVESTIGATE:
            return "investigate"
        elif score < self.THRESHOLD_RESPOND:
            return "respond"
        else:
            return "emergency"

    def _generate_explanation(self, signals: List[float], context: dict, score: float) -> str:
        """Generate human-readable explanation of the scoring result."""
        signals_array = np.array(signals[:29])
        top_indices = np.argsort(signals_array)[-3:][::-1]

        top_signals = []
        for idx in top_indices:
            # Find which layer this signal belongs to
            layer_name = None
            for layer, indices in self.LAYER_SIGNALS.items():
                if idx in indices:
                    layer_name = layer
                    break
            signal_name = f"D-{idx+1:02d}"
            top_signals.append(f"{signal_name}({signals_array[idx]:.2f})")

        level = self._map_to_level(score)
        asset_type = context.get("asset_type", "unknown")

        return (
            f"置信度 {score:.1%}，风险等级: {level}，"
            f"主要信号: {', '.join(top_signals)}，资产类型: {asset_type}"
        )

    def score(self, signals: List[float], context: dict) -> ConfidenceResult:
        """
        Compute confidence score from 35-dimensional input.

        Args:
            signals: 35-element list [29 detection signals + 6 context features]
            context: dict with hour_of_day, day_of_week, source_ip_count, asset_type

        Returns:
            ConfidenceResult with score, level, breakdown, and explanation
        """
        # Parse input: 29 detection signals + 6 context features
        detection_signals = np.array(signals[:29])
        context_features = self._normalize_context(context)

        # Combine into full 35-dim feature vector
        full_features = np.concatenate([detection_signals, context_features])

        # Weighted fusion using layer-normalized weights
        raw_score = np.dot(full_features, self.weights)

        # Apply Platt scaling calibration
        calibrated_score = self._platt_scaling(raw_score)

        # Map to response level
        level = self._map_to_level(calibrated_score)

        # Generate explanation
        explanation = self._generate_explanation(signals, context, calibrated_score)

        # Build breakdown
        breakdown = {
            "raw_score": float(raw_score),
            "weights": self.weights.tolist(),
            "layer_weights": self.LAYER_WEIGHTS,
            "context_features": context_features.tolist(),
        }

        return ConfidenceResult(
            score=calibrated_score,
            level=level,
            breakdown=breakdown,
            explanation=explanation,
        )


class LightGBMModel:
    """
    LightGBM model wrapper for D-25 fusion engine.

    This is a mock implementation. In production, this would load
    and run inference with a pre-trained LightGBM model.
    """

    def __init__(self, model_path: str = None):
        self.model_path = model_path
        self.model = None
        self._load_model()

    def _load_model(self):
        """Load pre-trained LightGBM model (mock implementation)."""
        # In production: self.model = lgb.Booster(model_file=self.model_path)
        self.model = "mock_model"

    def predict(self, features: np.ndarray) -> np.ndarray:
        """
        Run inference with LightGBM model.

        Args:
            features: numpy array of shape (n_samples, n_features)

        Returns:
            Predictions array of shape (n_samples,)
        """
        # Mock implementation: return weighted average
        # In production: return self.model.predict(features)
        if isinstance(features, list):
            features = np.array(features)
        if features.ndim == 1:
            features = features.reshape(1, -1)

        # Simple weighted sum as mock prediction
        weights = np.ones(features.shape[1]) / features.shape[1]
        return np.dot(features, weights)

    def predict_proba(self, features: np.ndarray) -> np.ndarray:
        """
        Run probability prediction with LightGBM model.

        Returns:
            Probability array of shape (n_samples, n_classes)
        """
        # Mock implementation
        pred = self.predict(features)
        return np.column_stack([1 - pred, pred])
