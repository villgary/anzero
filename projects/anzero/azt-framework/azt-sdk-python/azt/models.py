from dataclasses import dataclass
from enum import Enum
from typing import Optional


class Decision(Enum):
    ALLOW = "allow"
    DENY = "deny"
    REQUIRE_APPROVAL = "require_approval"
    UNSPECIFIED = "unspecified"


@dataclass
class ActionContext:
    agent_id: str
    action: str
    tool: str
    parameters: dict[str, str]
    trust_score: int
    session_id: str


@dataclass
class EnforcementResult:
    decision: Decision
    reason: str
    updated_trust_score: int
    request_id: str