import pytest
from app.detection_engine.rules.d01_tls_fingerprint import D01TLSFingerprint
from app.detection_engine.rules.d02_http_headers import D02HTTPHeaders
from app.detection_engine.rules.d03_request_timing import D03RequestTiming

@pytest.fixture
def d01():
    return D01TLSFingerprint()

@pytest.fixture
def d02():
    return D02HTTPHeaders()

@pytest.fixture
def d03():
    return D03RequestTiming()

def test_d01_match(d01):
    event = {"ja4": "t13d5f8g9h2", "ja3": "test"}
    result = d01.detect(event)
    assert result.matched is True
    assert result.rule_id == "D-01"
    assert result.confidence > 0.5

def test_d01_no_match(d01):
    event = {"ja4": "unknown", "ja3": "test"}
    result = d01.detect(event)
    assert result.matched is False

def test_d02_python_requests(d02):
    event = {"headers": {"user-agent": "python-requests/2.28.0"}}
    result = d02.detect(event)
    assert result.matched is True

def test_d03_react_pattern(d03):
    event = {"intervals": [10, 12, 11, 13, 10, 12, 11]}
    result = d03.detect(event)
    assert result.matched is True
    assert result.metadata["react_pattern"] is True
