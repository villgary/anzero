import pytest
import numpy as np
from app.detection_engine.d25.fusion_engine import FusionEngine

@pytest.fixture
def engine():
    return FusionEngine()

def test_fusion_35_dimensions(engine):
    # 35维输入信号
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