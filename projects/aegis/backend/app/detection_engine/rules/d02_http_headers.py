from .base import BaseRule, DetectionResult

AI_TOOL_PATTERNS = [
    "ChatGPT",
    "Claude",
    "PentestGPT",
    "python-ai",
    "gpt",
    "OpenAI",
    "Anthropic",
]

class D02HTTPHeaders(BaseRule):
    def __init__(self):
        super().__init__("D-02", "HTTP Headers Pattern Analysis")

    async def detect(self, event: dict) -> DetectionResult:
        headers = event.get("headers", {})
        user_agent = headers.get("user-agent", "")

        matched = False
        metadata = {}

        for pattern in AI_TOOL_PATTERNS:
            if pattern.lower() in user_agent.lower():
                matched = True
                metadata = {"pattern": pattern, "user_agent": user_agent}
                break

        return DetectionResult(
            rule_id=self.rule_id,
            confidence=0.90 if matched else 0.0,
            metadata=metadata,
            matched=matched
        )
