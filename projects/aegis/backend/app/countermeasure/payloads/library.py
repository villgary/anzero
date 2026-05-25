from dataclasses import dataclass
from typing import Optional

@dataclass
class PayloadTemplate:
    id: str
    name: str
    template: str
    target_types: list[str]

class PayloadLibrary:
    def __init__(self):
        self.templates = {
            "pi_injection": [
                PayloadTemplate(
                    id="pi-001",
                    name="HTML Comment Injection",
                    template='<script>/* {INJECTION_POINT} */</script>',
                    target_types=["html", "javascript"]
                ),
                PayloadTemplate(
                    id="pi-002",
                    name="JSON Field Injection",
                    template='{"status": "ok", "data": "{INJECTION_POINT}"}',
                    target_types=["json", "api"]
                ),
            ]
        }

    def get_templates(self, category: str) -> list[PayloadTemplate]:
        return self.templates.get(category, [])

    def select_payload(self, category: str, target_type: str) -> Optional[PayloadTemplate]:
        templates = self.get_templates(category)
        for t in templates:
            if target_type in t.target_types:
                return t
        return templates[0] if templates else None
