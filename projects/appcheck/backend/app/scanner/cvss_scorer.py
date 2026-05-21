from typing import Dict, Optional, Tuple
import math


class CVSSScorer:
    """CVSS 3.1 scoring calculator with full vector support."""

    SEVERITY_LEVELS = {
        (9.0, 10.0): "critical",
        (7.0, 8.9): "high",
        (4.0, 6.9): "medium",
        (0.1, 3.9): "low",
        (0.0, 0.0): "info",
    }

    # CVSS 3.1 metric values
    METRICS = {
        "AV": {"N": 0.85, "A": 0.62, "L": 0.55, "P": 0.20},
        "AC": {"L": 0.77, "H": 0.44},
        "PR": {"N": 0.85, "L": 0.62, "H": 0.27},  # Unchanged scope
        "UI": {"N": 0.85, "R": 0.62},
        "C": {"H": 0.56, "L": 0.22, "N": 0.0},
        "I": {"H": 0.56, "L": 0.22, "N": 0.0},
        "A": {"H": 0.56, "L": 0.22, "N": 0.0},
    }

    # CWE to CVSS base metrics mapping
    CWE_CVSS_MAPPING = {
        "CWE-79": {"AV": "N", "AC": "L", "C": "L", "I": "L", "A": "N"},  # XSS
        "CWE-89": {"AV": "N", "AC": "L", "C": "H", "I": "H", "A": "H"},  # SQL Injection
        "CWE-306": {"AV": "N", "AC": "L", "PR": "N", "I": "H", "A": "H"},  # Auth missing
        "CWE-862": {"AV": "N", "AC": "L", "PR": "N", "I": "N", "A": "N"},  # Auth missing
        "CWE-798": {"AV": "N", "AC": "L", "PR": "N", "I": "H", "A": "H"},  # Hardcoded credentials
        "CWE-259": {"AV": "N", "AC": "L", "PR": "N", "I": "H", "A": "H"},  # Hardcoded password
        "CWE-200": {"AV": "N", "AC": "L", "PR": "N", "I": "H", "A": "N"},  # Info disclosure
        "CWE-310": {"AV": "N", "AC": "L", "C": "H", "I": "N", "A": "N"},  # Weak crypto
        "CWE-326": {"AV": "N", "AC": "L", "C": "L", "I": "L", "A": "L"},  # Weak encryption
        "CWE-327": {"AV": "N", "AC": "L", "C": "H", "I": "H", "A": "H"},  # Broken crypto
        "CWE-295": {"AV": "N", "AC": "L", "C": "H", "I": "H", "A": "N"},  # Cert validation
        "CWE-297": {"AV": "N", "AC": "H", "C": "H", "I": "H", "A": "N"},  # Cert mismatch
        "CWE-345": {"AV": "N", "AC": "L", "C": "H", "I": "H", "A": "H"},  # Insufficient verification
        "CWE-346": {"AV": "N", "AC": "L", "C": "H", "I": "H", "A": "N"},  # Origin validation
        "CWE-347": {"AV": "N", "AC": "L", "C": "H", "I": "N", "A": "N"},  # Crypto verification
        "CWE-354": {"AV": "N", "AC": "L", "C": "H", "I": "H", "A": "H"},  # Int overflow
        "CWE-190": {"AV": "N", "AC": "L", "C": "H", "I": "H", "A": "H"},  # Int overflow
        "CWE-191": {"AV": "N", "AC": "L", "C": "H", "I": "H", "A": "H"},  # Int underflow
        "CWE-369": {"AV": "N", "AC": "L", "C": "L", "I": "L", "A": "L"},  # Divide by zero
        "CWE-94": {"AV": "N", "AC": "L", "C": "H", "I": "H", "A": "H"},  # Code injection
        "CWE-95": {"AV": "N", "AC": "L", "C": "H", "I": "H", "A": "H"},  # Eval injection
        "CWE-78": {"AV": "N", "AC": "L", "C": "H", "I": "H", "A": "H"},  # OS command injection
        "CWE-88": {"AV": "N", "AC": "L", "C": "H", "I": "H", "A": "H"},  # Arg injection
        "CWE-90": {"AV": "N", "AC": "L", "C": "H", "I": "H", "A": "H"},  # LDAP injection
        "CWE-643": {"AV": "N", "AC": "L", "C": "H", "I": "H", "A": "H"},  # XPath injection
        "CWE-99": {"AV": "N", "AC": "L", "C": "H", "I": "H", "A": "H"},  # Resource injection
        "CWE-601": {"AV": "N", "AC": "L", "PR": "N", "UI": "R", "C": "L", "I": "L", "A": "N"},  # Open redirect
        "CWE-862": {"AV": "N", "AC": "L", "PR": "N", "I": "N", "A": "N"},  # Auth missing
        "CWE-639": {"AV": "N", "AC": "L", "PR": "L", "I": "H", "A": "N"},  # Auth bypass
        "CWE-284": {"AV": "N", "AC": "L", "PR": "H", "I": "H", "A": "H"},  # Access control
        "CWE-285": {"AV": "N", "AC": "L", "PR": "N", "I": "H", "A": "H"},  # Auth bypass
        "CWE-287": {"AV": "N", "AC": "L", "PR": "N", "I": "H", "A": "H"},  # Auth bypass
        "CWE-290": {"AV": "N", "AC": "H", "PR": "N", "I": "H", "A": "H"},  # Auth bypass
        "CWE-294": {"AV": "N", "AC": "H", "PR": "N", "I": "H", "A": "H"},  # Auth bypass
        "CWE-302": {"AV": "N", "AC": "L", "PR": "N", "I": "H", "A": "N"},  # Auth bypass
        "CWE-303": {"AV": "N", "AC": "L", "PR": "N", "I": "H", "A": "H"},  # Auth bypass
        "CWE-304": {"AV": "N", "AC": "L", "PR": "N", "I": "H", "A": "H"},  # Auth bypass
        "CWE-523": {"AV": "N", "AC": "L", "PR": "N", "I": "H", "A": "N"},  # Cred in code
        "CWE-312": {"AV": "N", "AC": "L", "C": "H", "I": "N", "A": "N"},  # Cleartext storage
        "CWE-315": {"AV": "N", "AC": "L", "C": "H", "I": "H", "A": "N"},  # Cleartext cookie
        "CWE-316": {"AV": "N", "AC": "L", "C": "H", "I": "N", "A": "N"},  # Cleartext memory
        "CWE-317": {"AV": "N", "AC": "L", "C": "H", "I": "N", "A": "N"},  # Cleartext GUI
        "CWE-318": {"AV": "N", "AC": "L", "C": "H", "I": "N", "A": "N"},  # Cleartext config
        "CWE-359": {"AV": "N", "AC": "L", "PR": "L", "I": "H", "A": "N"},  # Privilege escrow
        "CWE-489": {"AV": "L", "AC": "L", "PR": "N", "I": "H", "A": "H"},  # Debug enabled
        "CWE-509": {"AV": "N", "AC": "L", "PR": "N", "I": "H", "A": "N"},  # Repudiation
        "CWE-404": {"AV": "N", "AC": "L", "PR": "N", "I": "N", "A": "H"},  # Resource exhaustion
        "CWE-770": {"AV": "N", "AC": "L", "PR": "N", "I": "N", "A": "H"},  # Resource exhaustion
        "CWE-835": {"AV": "N", "AC": "L", "PR": "N", "I": "N", "A": "H"},  # Loop infinite
        "CWE-772": {"AV": "N", "AC": "L", "PR": "N", "I": "N", "A": "N"},  # Resource not released
    }

    @staticmethod
    def get_severity(score: Optional[float]) -> str:
        if score is None:
            return "info"
        for (low, high), severity in CVSSScorer.SEVERITY_LEVELS.items():
            if low <= score <= high:
                return severity
        return "info"

    @classmethod
    def calculate_cvss(cls, vector: Dict[str, str]) -> float:
        """Calculate CVSS base score from vector metrics."""
        if not vector:
            return 0.0

        # Get metric values
        av = cls.METRICS["AV"].get(vector.get("AV", "N"), 0.85)
        ac = cls.METRICS["AC"].get(vector.get("AC", "L"), 0.77)
        pr = cls.METRICS["PR"].get(vector.get("PR", "N"), 0.85)
        ui = cls.METRICS["UI"].get(vector.get("UI", "N"), 0.85)
        c = cls.METRICS["C"].get(vector.get("C", "N"), 0.0)
        i = cls.METRICS["I"].get(vector.get("I", "N"), 0.0)
        a = cls.METRICS["A"].get(vector.get("A", "N"), 0.0)

        # Calculate impact
        impact = 1 - (1 - c) * (1 - i) * (1 - a)

        # Calculate exploitability
        exploitability = 8.22 * av * ac * pr * ui

        # Calculate base score
        if impact <= 0:
            return 0.0

        base_score = min(1.08 * (impact + exploitability), 10.0)
        return round(base_score, 1)

    @classmethod
    def get_vector_for_finding(cls, finding_type: str, context: Dict = None) -> Tuple[float, str]:
        """Get CVSS score and vector string for a finding type."""
        context = context or {}

        # Check CWE mapping first
        cwe_id = context.get("cwe_id")
        if cwe_id and cwe_id in cls.CWE_CVSS_MAPPING:
            vector = cls.CWE_CVSS_MAPPING[cwe_id].copy()
            # Adjust based on context
            if context.get("network_available"):
                vector["AV"] = "N"
            elif context.get("adjacent_network"):
                vector["AV"] = "A"
            elif context.get("local_access"):
                vector["AV"] = "L"
            else:
                vector["AV"] = "N"

            if context.get("high_privileges"):
                vector["PR"] = "H"
            elif context.get("low_privileges"):
                vector["PR"] = "L"
            else:
                vector["PR"] = "N"

            if context.get("user_interaction_required"):
                vector["UI"] = "R"
            else:
                vector["UI"] = "N"

            score = cls.calculate_cvss(vector)
            vector_str = "/".join([f"{k}:{v}" for k, v in sorted(vector.items())])
            return score, vector_str

        # Default scoring based on finding type
        default_scores = {
            "debuggable": (5.0, "AV:N/AC:L/PR:N/UI:N/C:L/I:L/A:L"),
            "cleartext_traffic": (5.5, "AV:N/AC:L/PR:N/UI:N/C:L/I:L/A:L"),
            "allow_backup": (2.0, "AV:N/AC:L/PR:N/UI:N/C:L/I:N/A:N"),
            "test_only": (4.0, "AV:N/AC:L/PR:N/UI:N/C:L/I:L/A:N"),
            "no_network_config": (3.0, "AV:N/AC:L/PR:N/UI:N/C:L/I:N/A:N"),
            "dangerous_permission": (7.0, "AV:N/AC:L/PR:N/UI:N/C:H/I:H/A:H"),
            "signature_mismatch": (7.5, "AV:N/AC:H/PR:N/UI:N/C:H/I:H/A:N"),
            "self_signed_cert": (6.5, "AV:N/AC:L/PR:N/UI:N/C:L/I:H/A:N"),
            "expired_cert": (5.5, "AV:N/AC:L/PR:N/UI:N/C:L/I:H/A:N"),
            "hardcoded_secret": (8.5, "AV:N/AC:L/PR:N/UI:N/C:H/I:H/A:H"),
            "native_code": (6.0, "AV:N/AC:L/PR:N/UI:N/C:L/I:L/A:L"),
            "webview_javascript": (7.0, "AV:N/AC:L/PR:N/UI:R/C:H/I:H/A:H"),
            "crypto_weak": (5.5, "AV:N/AC:L/PR:N/UI:N/C:L/I:L/A:N"),
            "insecure_storage": (6.5, "AV:N/AC:L/PR:N/UI:N/C:L/I:H/A:N"),
        }

        if finding_type in default_scores:
            return default_scores[finding_type]

        return 5.0, "AV:N/AC:L/PR:N/UI:N/C:L/I:L/A:L"

    @staticmethod
    def severity_to_cvss(severity: str) -> float:
        """Convert severity level to approximate CVSS score."""
        mapping = {
            "critical": 9.5,
            "high": 7.5,
            "medium": 5.0,
            "low": 2.5,
            "info": 0.0,
        }
        return mapping.get(severity.lower(), 5.0)
