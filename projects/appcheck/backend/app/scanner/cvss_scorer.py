from typing import Optional

class CVSSScorer:
    """CVSS 3.1 scoring calculator."""

    SEVERITY_LEVELS = {
        (9.0, 10.0): "critical",
        (7.0, 8.9): "high",
        (4.0, 6.9): "medium",
        (0.1, 3.9): "low",
        (0.0, 0.0): "info",
    }

    @staticmethod
    def get_severity(score: Optional[float]) -> str:
        if score is None:
            return "info"
        for (low, high), severity in CVSSScorer.SEVERITY_LEVELS.items():
            if low <= score <= high:
                return severity
        return "info"
