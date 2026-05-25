from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

@dataclass
class DetectionResult:
    rule_id: str
    confidence: float
    metadata: dict = field(default_factory=dict)
    matched: bool = False

class BaseRule(ABC):
    def __init__(self, rule_id: str, name: str):
        self.rule_id = rule_id
        self.name = name

    @abstractmethod
    async def detect(self, event: dict) -> DetectionResult:
        pass
