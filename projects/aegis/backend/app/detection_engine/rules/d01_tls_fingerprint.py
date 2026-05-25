from .base import BaseRule, DetectionResult

KNOWN_TOOLS = {
    "pentestgpt": ["t13d5f8g9h2", "t13d5f8g9h3"],
    "nmap": ["t13d000000", "t13d111111"],
    "shannon": ["t13dshack1", "t13dshack2"],
}

class D01TLSFingerprint(BaseRule):
    def __init__(self):
        super().__init__("D-01", "TLS Fingerprint Match")

    async def detect(self, event: dict) -> DetectionResult:
        ja4 = event.get("ja4", "")
        ja3 = event.get("ja3", "")

        matched_tool = None
        for tool, fingerprints in KNOWN_TOOLS.items():
            if ja4 in fingerprints or ja3 in fingerprints:
                matched_tool = tool
                break

        if matched_tool:
            return DetectionResult(
                rule_id=self.rule_id,
                confidence=0.95,
                metadata={"tool": matched_tool, "ja4": ja4, "ja3": ja3},
                matched=True
            )

        return DetectionResult(
            rule_id=self.rule_id,
            confidence=0.0,
            metadata={"ja4": ja4, "ja3": ja3},
            matched=False
        )
