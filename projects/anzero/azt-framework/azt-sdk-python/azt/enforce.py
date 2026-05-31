import time
import uuid
from typing import Optional

from azt.client import AZTClient
from azt.config import SDKConfig
from azt.models import ActionContext, Decision, EnforcementResult


class AZTEnforcer:
    def __init__(self, config: SDKConfig):
        self.config = config
        self.client = AZTClient(config)

    def check_action(
        self,
        action: str,
        tool: str,
        parameters: Optional[dict[str, str]] = None,
        trust_score: Optional[int] = None,
    ) -> EnforcementResult:
        context = ActionContext(
            agent_id=self.config.agent_id or "unknown",
            action=action,
            tool=tool,
            parameters=parameters or {},
            trust_score=trust_score or self.config.default_trust_score,
            session_id=self.config.session_id or str(uuid.uuid4()),
        )
        return self.client.enforce(context)

    def close(self):
        self.client.close()


def enforce_action(
    action: str,
    tool: str,
    gateway_addr: str = "localhost:50051",
    agent_id: Optional[str] = None,
    **kwargs,
) -> EnforcementResult:
    config = SDKConfig(gateway_addr=gateway_addr, agent_id=agent_id, **kwargs)
    enforcer = AZTEnforcer(config)
    try:
        return enforcer.check_action(action, tool)
    finally:
        enforcer.close()