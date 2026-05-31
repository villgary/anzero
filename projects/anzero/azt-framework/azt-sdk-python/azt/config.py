from dataclasses import dataclass
from typing import Optional


@dataclass
class SDKConfig:
    gateway_addr: str = "localhost:50051"
    default_trust_score: int = 70
    timeout_seconds: float = 5.0
    agent_id: Optional[str] = None
    session_id: Optional[str] = None

    def validate(self) -> None:
        if not self.gateway_addr:
            raise ValueError("gateway_addr is required")
        if not 0 <= self.default_trust_score <= 100:
            raise ValueError("trust_score must be between 0 and 100")