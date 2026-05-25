from dataclasses import dataclass
from enum import Enum
from typing import Optional


class ResponseLevel(Enum):
    GREEN = "green"   # 自动执行
    YELLOW = "yellow" # 需SOC审批
    RED = "red"       # 需CISO审批


@dataclass
class CountermeasureDecision:
    level: ResponseLevel
    approval_required: bool
    approver: Optional[str]  # None, "soc", "ciso"
    countermeasures: list[str]  # C-01, C-04等


class DecisionTree:
    def decide(self, confidence: float, _attack_type: str) -> CountermeasureDecision:
        if confidence < 0 or confidence > 1:
            raise ValueError("confidence must be between 0 and 1")

        if confidence < 0.30:
            # observe - no action needed
            return CountermeasureDecision(
                level=ResponseLevel.GREEN,  # Using GREEN as placeholder for observe
                approval_required=False,
                approver=None,
                countermeasures=[]
            )
        elif confidence < 0.60:
            return CountermeasureDecision(
                level=ResponseLevel.GREEN,
                approval_required=False,
                approver=None,
                countermeasures=["C-01", "C-04"]
            )
        elif confidence < 0.85:
            return CountermeasureDecision(
                level=ResponseLevel.YELLOW,
                approval_required=True,
                approver="soc",
                countermeasures=["C-13", "C-25"]
            )
        else:
            return CountermeasureDecision(
                level=ResponseLevel.RED,
                approval_required=True,
                approver="ciso",
                countermeasures=["C-18", "C-22", "C-24"]
            )