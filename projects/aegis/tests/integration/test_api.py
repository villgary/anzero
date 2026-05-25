import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_dashboard_stats():
    response = client.get("/api/v1/dashboard/stats")
    assert response.status_code == 200
    data = response.json()
    assert "attackCount" in data


def test_detect_valid_input():
    """Test POST /api/v1/detect with valid signals and context."""
    valid_signals = [0.2] * 29 + [0.5, 0.5, 0.5, 0.5, 0.5, 0.5]
    valid_context = {
        "hour_of_day": 14,
        "day_of_week": 3,
        "source_ip_count": 5,
        "asset_type": "web"
    }
    response = client.post("/api/v1/detect", json={
        "signals": valid_signals,
        "context": valid_context
    })
    assert response.status_code == 200
    data = response.json()
    assert "confidence" in data
    assert "level" in data
    assert isinstance(data["confidence"], float)
    assert data["level"] in ["observe", "investigate", "respond", "emergency"]


def test_detect_missing_signals():
    """Test that missing signals field returns 422 validation error."""
    valid_context = {
        "hour_of_day": 14,
        "day_of_week": 3,
        "source_ip_count": 5,
        "asset_type": "web"
    }
    response = client.post("/api/v1/detect", json={
        "context": valid_context
    })
    assert response.status_code == 422


def test_detect_missing_context():
    """Test that missing context field returns 422 validation error."""
    valid_signals = [0.2] * 35
    response = client.post("/api/v1/detect", json={
        "signals": valid_signals
    })
    assert response.status_code == 422


def test_detect_invalid_signals_type():
    """Test that non-list signals returns 422 validation error."""
    response = client.post("/api/v1/detect", json={
        "signals": "not a list",
        "context": {}
    })
    assert response.status_code == 422


def test_detect_invalid_context_type():
    """Test that non-dict context returns 422 validation error."""
    response = client.post("/api/v1/detect", json={
        "signals": [0.2] * 35,
        "context": "not a dict"
    })
    assert response.status_code == 422


def test_detect_invalid_signal_element():
    """Test that non-numeric signal element returns 422 validation error."""
    response = client.post("/api/v1/detect", json={
        "signals": [0.2, "invalid", 0.3] + [0.2] * 32,
        "context": {"asset_type": "web"}
    })
    assert response.status_code == 422
