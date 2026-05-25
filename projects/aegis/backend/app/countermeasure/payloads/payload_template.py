from dataclasses import dataclass

@dataclass
class PayloadTemplate:
    id: str
    name: str
    template: str
    target_types: list[str]
    severity: str = "medium"  # low/medium/high/critical
