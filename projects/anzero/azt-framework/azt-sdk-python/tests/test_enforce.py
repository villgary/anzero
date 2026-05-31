import pytest
from azt.enforce import AZTEnforcer
from azt.config import SDKConfig
from azt.models import Decision


class TestAZTEnforcer:
    def test_check_action_returns_result(self):
        config = SDKConfig(gateway_addr="localhost:50051")
        enforcer = AZTEnforcer(config)
        result = enforcer.check_action("tool_call", "read")
        assert isinstance(result.decision, Decision)
        enforcer.close()