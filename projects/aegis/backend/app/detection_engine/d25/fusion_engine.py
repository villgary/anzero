import numpy as np
from dataclasses import dataclass
from typing import List

@dataclass
class ConfidenceResult:
    score: float
    level: str
    breakdown: dict
    explanation: str

class FusionEngine:
    LAYER_WEIGHTS = {
        "L1": 0.15, "L2": 0.25, "L3": 0.15, "L4": 0.20, "L5": 0.15
    }

    def __init__(self):
        self.weights = np.array([0.15, 0.25, 0.15, 0.20, 0.15, 0.10])

    def score(self, signals: List[float], context: dict) -> ConfidenceResult:
        signals_array = np.array(signals[:29])
        context_array = self._encode_context(context)
        full_input = np.concatenate([signals_array, context_array])

        # 简化的加权融合（实际生产用LightGBM模型）
        # 使用context weights进行上下文感知的加权
        weighted = np.dot(context_array, self.weights)
        calibrated = self._platt_scaling(weighted)

        level = self._map_to_level(calibrated)
        explanation = self._generate_explanation(signals, calibrated)

        return ConfidenceResult(
            score=calibrated,
            level=level,
            breakdown={"weights": self.weights.tolist()},
            explanation=explanation
        )

    def _platt_scaling(self, raw: float) -> float:
        return min(1.0, max(0.0, raw))

    def _map_to_level(self, score: float) -> str:
        if score < 0.30: return "observe"
        if score < 0.60: return "investigate"
        if score < 0.85: return "respond"
        return "emergency"

    def _encode_context(self, context: dict) -> np.ndarray:
        return np.array([
            context.get("hour_of_day", 0) / 24.0,
            context.get("day_of_week", 0) / 7.0,
            min(context.get("source_ip_count", 0), 10) / 10.0,
            1.0 if context.get("asset_type") == "web" else 0.0,
            1.0 if context.get("asset_type") == "api" else 0.0,
            1.0 if context.get("asset_type") == "db" else 0.0,
        ])

    def _generate_explanation(self, signals: List[float], score: float) -> str:
        top_signals = sorted(enumerate(signals[:29]), key=lambda x: x[1], reverse=True)[:3]
        parts = [f"信号{i+1}({v:.2f})" for i, v in top_signals]
        return f"置信度 {score:.0%}，主要信号：{', '.join(parts)}"
