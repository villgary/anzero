import pytest
from azt.client import AZTClient
from azt.config import SDKConfig
from azt.models import ActionContext, Decision


class TestSDKConfig:
    def test_default_config(self):
        config = SDKConfig()
        assert config.gateway_addr == "localhost:50051"
        assert config.default_trust_score == 70

    def test_config_validation_valid(self):
        config = SDKConfig(gateway_addr="localhost:50051", default_trust_score=50)
        config.validate()  # Should not raise

    def test_config_validation_invalid_score(self):
        config = SDKConfig(default_trust_score=150)
        with pytest.raises(ValueError, match="trust_score must be between"):
            config.validate()


class TestActionContext:
    def test_create_context(self):
        ctx = ActionContext(
            agent_id="test-agent",
            action="tool_call",
            tool="send_email",
            parameters={"to": "user@example.com"},
            trust_score=70,
            session_id="session-123",
        )
        assert ctx.agent_id == "test-agent"
        assert ctx.tool == "send_email"
        assert ctx.trust_score == 70