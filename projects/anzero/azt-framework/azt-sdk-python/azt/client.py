import sys
import time
from pathlib import Path

# Add proto directory to path for gRPC imports
# proto is at azt-framework/proto/, so we add azt-framework/
_sdk_dir = Path(__file__).parent.parent
_framework_dir = _sdk_dir.parent
_proto_dir = _framework_dir / "proto"
sys.path.insert(0, str(_framework_dir))

import grpc
from proto.azt_pb2 import (
    ActionContext as pb2_ActionContext,
    EnforcementRequest,
    TrustScoreRequest,
    Decision as pb2_Decision,
)
from proto.azt_pb2_grpc import AZTGatewayStub

from azt.config import SDKConfig
from azt.models import ActionContext, Decision, EnforcementResult


class AZTClient:
    def __init__(self, config: SDKConfig):
        self.config = config
        self.channel = grpc.insecure_channel(config.gateway_addr)
        self.stub = AZTGatewayStub(self.channel)

    def enforce(self, context: ActionContext) -> EnforcementResult:
        req = EnforcementRequest(
            context=pb2_ActionContext(
                agent_id=context.agent_id,
                action=context.action,
                tool=context.tool,
                parameters=context.parameters,
                trust_score=context.trust_score,
                session_id=context.session_id,
                timestamp=int(time.time()),
            )
        )
        resp = self.stub.Enforce(req, timeout=self.config.timeout_seconds)
        return EnforcementResult(
            decision=Decision(resp.decision.name.lower()),
            reason=resp.reason,
            updated_trust_score=resp.updated_trust_score,
            request_id=resp.request_id,
        )

    def get_trust_score(self, agent_id: str) -> tuple[int, str]:
        req = TrustScoreRequest(agent_id=agent_id)
        resp = self.stub.GetTrustScore(req, timeout=self.config.timeout_seconds)
        return resp.score, resp.reason

    def close(self):
        self.channel.close()