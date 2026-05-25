"""
LightGBM model wrapper for D-25 Confidence Fusion Engine.

This module provides the LightGBMModel class for loading pre-trained
models and running inference. In production, replace the mock
implementation with actual LightGBM model loading.
"""

import numpy as np
from typing import Optional, List, Union


class LightGBMModel:
    """
    LightGBM model wrapper for D-25 fusion engine.

    Provides inference interface for pre-trained LightGBM models
    used in the confidence scoring pipeline.
    """

    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize LightGBM model wrapper.

        Args:
            model_path: Path to pre-trained LightGBM model file.
                       If None, uses mock implementation.
        """
        self.model_path = model_path
        self.model = None
        self.n_features = 35
        self._load_model()

    def _load_model(self):
        """
        Load pre-trained LightGBM model.

        In production, this would load an actual model:
            import lightgbm as lgb
            self.model = lgb.Booster(model_file=self.model_path)
        """
        if self.model_path:
            # Production: load actual model
            # self.model = lgb.Booster(model_file=self.model_path)
            pass
        else:
            # Mock mode for testing/development
            self.model = MockLightGBMModel(self.n_features)

    def predict(self, features: Union[np.ndarray, List[float]]) -> np.ndarray:
        """
        Run inference with LightGBM model.

        Args:
            features: Input features, shape (n_samples, n_features) or (n_features,)

        Returns:
            Predictions array of shape (n_samples,)
        """
        if isinstance(features, list):
            features = np.array(features)

        if features.ndim == 1:
            features = features.reshape(1, -1)

        return self.model.predict(features)

    def predict_proba(self, features: Union[np.ndarray, List[float]]) -> np.ndarray:
        """
        Run probability prediction with LightGBM model.

        Args:
            features: Input features, shape (n_samples, n_features)

        Returns:
            Probability array of shape (n_samples, 2) with columns [negative, positive]
        """
        if isinstance(features, list):
            features = np.array(features)

        if features.ndim == 1:
            features = features.reshape(1, -1)

        return self.model.predict_proba(features)

    def get_feature_importance(self) -> np.ndarray:
        """
        Get feature importance scores from the model.

        Returns:
            Array of shape (n_features,) with importance scores
        """
        if self.model_path and self.model is not None:
            # Production: return self.model.feature_importance()
            pass
        return np.ones(self.n_features) / self.n_features


class MockLightGBMModel:
    """
    Mock LightGBM model for testing and development.

    Implements a simple weighted average for demonstration purposes.
    """

    def __init__(self, n_features: int):
        self.n_features = n_features
        self.weights = np.random.rand(n_features)
        self.weights /= self.weights.sum()

    def predict(self, features: np.ndarray) -> np.ndarray:
        """Mock prediction using weighted average."""
        return np.dot(features, self.weights)

    def predict_proba(self, features: np.ndarray) -> np.ndarray:
        """Mock probability prediction using sigmoid on weighted sum."""
        raw = np.dot(features, self.weights)
        prob = 1.0 / (1.0 + np.exp(-raw))
        return np.column_stack([1 - prob, prob])
