from dataclasses import dataclass
from enum import Enum
from typing import Optional


class ResponseLevel(Enum):
    GREEN = "green"
    YELLOW = "yellow"
    RED = "red"


@dataclass
class CountermeasureDecision:
    level: str
    approval_required: bool
    approver: Optional[str]
    countermeasures: list[str]


class DecisionTree:
    def decide(self, confidence: float, attack_type: str) -> CountermeasureDecision:
        if confidence < 0.30:
            return CountermeasureDecision("observe", False, None, [])
        elif confidence < 0.60:
            return CountermeasureDecision("green", False, None, ["C-01", "C-04"])
        elif confidence < 0.85:
            return CountermeasureDecision("yellow", True, "soc", ["C-13", "C-25"])
        else:
            return CountermeasureDecision("red", True, "ciso", ["C-18", "C-22", "C-24"])
