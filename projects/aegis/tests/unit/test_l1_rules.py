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


@pytest.mark.asyncio
async def test_d01_match(d01):
    event = {"ja4": "t13d5f8g9h2", "ja3": "test"}
    result = await d01.detect(event)
    assert result.matched is True
    assert result.rule_id == "D-01"
    assert result.confidence > 0.5


@pytest.mark.asyncio
async def test_d01_no_match(d01):
    event = {"ja4": "unknown", "ja3": "unknown"}
    result = await d01.detect(event)
    assert result.matched is False


@pytest.mark.asyncio
async def test_d01_ja3_match(d01):
    event = {"ja4": "unknown", "ja3": "t13d5f8g9h2"}
    result = await d01.detect(event)
    assert result.matched is True
    assert result.rule_id == "D-01"


@pytest.mark.asyncio
async def test_d02_ai_tool_chatgpt(d02):
    event = {"headers": {"user-agent": "ChatGPT/1.0"}}
    result = await d02.detect(event)
    assert result.matched is True
    assert result.metadata["pattern"] == "ChatGPT"


@pytest.mark.asyncio
async def test_d02_ai_tool_claude(d02):
    event = {"headers": {"user-agent": "Claude/1.0"}}
    result = await d02.detect(event)
    assert result.matched is True
    assert result.metadata["pattern"] == "Claude"


@pytest.mark.asyncio
async def test_d02_ai_tool_pentestgpt(d02):
    event = {"headers": {"user-agent": "PentestGPT/0.1"}}
    result = await d02.detect(event)
    assert result.matched is True
    assert result.metadata["pattern"] == "PentestGPT"


@pytest.mark.asyncio
async def test_d03_bot_regular_timing(d03):
    """Bot with fixed delays has regular timing (low stdev) - should NOT match AI think-burst"""
    event = {"intervals": [10, 12, 11, 13, 10, 12, 11]}
    result = await d03.detect(event)
    assert result.matched is False
    assert result.metadata["react_pattern"] is False


@pytest.mark.asyncio
async def test_d03_ai_think_burst(d03):
    """AI think-burst pattern: bursts with 5-30s pauses = irregular timing (high stdev)"""
    # Burst pattern: short gaps within bursts + long pauses for LLM inference
    event = {"intervals": [1, 9, 28, 2, 18, 30, 5, 14, 27, 3]}
    result = await d03.detect(event)
    assert result.matched is True
    assert result.metadata["react_pattern"] is True
