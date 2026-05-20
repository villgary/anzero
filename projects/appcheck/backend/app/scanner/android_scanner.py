from typing import Dict, List
from androguard.misc import AnalyzeAPK
from .manifest_parser import ManifestParser
from .permission_analyzer import PermissionAnalyzer
from .security_checks import SecurityChecker
from .sdk_detector import SDKDetector
from .cvss_scorer import CVSSScorer


class AndroidScanner:
    def __init__(self, apk_path: str):
        self.apk_path = apk_path
        self.parser = ManifestParser()
        self.permission_analyzer = PermissionAnalyzer()
        self.security_checker = SecurityChecker()
        self.sdk_detector = SDKDetector()

    def scan(self) -> Dict:
        # Analyze APK
        a, d, dx = AnalyzeAPK(self.apk_path)

        # Parse manifest
        manifest = self.parser.parse(dx)

        # Analyze permissions
        permission_findings = self.permission_analyzer.analyze(manifest["permissions"])

        # Run security checks
        security_findings = self.security_checker.run_checks(dx)

        # Detect SDKs
        sdk_info = self.sdk_detector.detect(dx)

        # Combine findings
        all_findings = []
        for pf in permission_findings:
            all_findings.append({
                "category": "permission",
                "severity": pf["severity"],
                "title": f"Dangerous Permission: {pf['permission']}",
                "description": pf["description"],
                "cvss_score": {"critical": 9.0, "high": 7.5, "medium": 5.0, "low": 2.5}.get(pf["severity"], 5.0),
                "remediation": f"Review necessity of {pf['permission']}",
            })

        for sf in security_findings:
            all_findings.append(sf)

        # Calculate overall risk score
        if all_findings:
            max_score = max(f["cvss_score"] for f in all_findings)
            avg_score = sum(f["cvss_score"] for f in all_findings) / len(all_findings)
            risk_score = round(max_score * 0.7 + avg_score * 0.3, 1)
        else:
            risk_score = 0.0

        return {
            "manifest": manifest,
            "sdk_count": sdk_info["count"],
            "findings": all_findings,
            "risk_score": risk_score,
        }
