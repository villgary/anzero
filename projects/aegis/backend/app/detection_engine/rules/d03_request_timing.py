from .base import BaseRule, DetectionResult
import statistics

class D03RequestTiming(BaseRule):
    def __init__(self):
        super().__init__("D-03", "Request Timing Pattern Analysis")

    async def detect(self, event: dict) -> DetectionResult:
        intervals = event.get("intervals", [])

        if len(intervals) < 5:
            return DetectionResult(
                rule_id=self.rule_id,
                confidence=0.0,
                metadata={"reason": "insufficient_data"},
                matched=False
            )

        mean_interval = statistics.mean(intervals)
        stdev_interval = statistics.stdev(intervals) if len(intervals) > 1 else 0

        react_pattern = (5 <= mean_interval <= 30) and (stdev_interval < 10)

        return DetectionResult(
            rule_id=self.rule_id,
            confidence=0.85 if react_pattern else 0.0,
            metadata={
                "mean_interval": mean_interval,
                "stdev_interval": stdev_interval,
                "react_pattern": react_pattern
            },
            matched=react_pattern
        )
