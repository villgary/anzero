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
    UpdateTrustScoreRequest,
    GetAgentScoreRequest,
    TrustScoreResponse,
    FactorBreakdown,
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

    def update_trust_score(self, agent_id: str, factor: str, delta: int, reason: str, action_context: dict = None) -> dict:
        req = UpdateTrustScoreRequest(
            agent_id=agent_id,
            factor=factor,
            delta=delta,
            reason=reason,
            action_context=action_context or {},
        )
        resp = self.stub.UpdateTrustScore(req, timeout=self.config.timeout_seconds)
        return {
            "score": resp.score,
            "reason": resp.reason,
            "agent_id": resp.agent_id,
            "breakdown": {
                "identity": resp.breakdown.identity,
                "history": resp.breakdown.history,
                "time": resp.breakdown.time,
                "anomaly": resp.breakdown.anomaly,
                "frequency": resp.breakdown.frequency,
            } if resp.breakdown else None,
        }

    def get_agent_score(self, agent_id: str) -> dict:
        req = GetAgentScoreRequest(
            agent_id=agent_id,
        )
        resp = self.stub.GetAgentScore(req, timeout=self.config.timeout_seconds)
        return {
            "score": resp.score,
            "reason": resp.reason,
            "agent_id": resp.agent_id,
            "breakdown": {
                "identity": resp.breakdown.identity,
                "history": resp.breakdown.history,
                "time": resp.breakdown.time,
                "anomaly": resp.breakdown.anomaly,
                "frequency": resp.breakdown.frequency,
            } if resp.breakdown else None,
        }

    def close(self):
        self.channel.close()