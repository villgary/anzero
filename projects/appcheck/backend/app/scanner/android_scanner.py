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

        # Parse manifest - needs APK object
        manifest = self.parser.parse(a)

        # Analyze permissions
        permission_findings = self.permission_analyzer.analyze(manifest["permissions"])

        # Run security checks - needs APK object
        security_findings = self.security_checker.run_checks(a)

        # Detect SDKs - needs Analysis object
        sdk_info = self.sdk_detector.detect(dx)

        # Combine findings with proper CVSS calculation
        all_findings = []

        # Process permission findings
        for pf in permission_findings:
            # Calculate CVSS based on permission type
            severity = pf["severity"]
            cvss_score = CVSSScorer.severity_to_cvss(severity)
            cvss_vector = "AV:N/AC:L/PR:N/UI:N"

            # Adjust based on permission type
            if pf["permission"] in [
                "android.permission.READ_SMS",
                "android.permission.SEND_SMS",
                "android.permission.READ_CALL_LOG",
                "android.permission.WRITE_CALL_LOG",
                "android.permission.PROCESS_OUTGOING_CALLS",
            ]:
                cvss_score = 8.5
                cvss_vector = "AV:N/AC:L/PR:N/UI:N/C:H/I:H/A:H"
            elif pf["permission"] in [
                "android.permission.CAMERA",
                "android.permission.RECORD_AUDIO",
                "android.permission.ACCESS_FINE_LOCATION",
            ]:
                cvss_score = 7.0
                cvss_vector = "AV:N/AC:L/PR:N/UI:R/C:H/I:H/A:H"

            all_findings.append({
                "category": "permission",
                "severity": severity,
                "title": f"Dangerous Permission: {pf['permission']}",
                "description": pf["description"],
                "cvss_score": cvss_score,
                "cvss_vector": cvss_vector,
                "cwe_id": "CWE-276",  # Insecure Default Permissions
                "remediation": f"Review necessity of {pf['permission']}",
            })

        # Process security findings
        for sf in security_findings:
            # Ensure each finding has required fields
            finding = {
                "category": sf.get("category", "security"),
                "severity": sf.get("severity", "medium"),
                "title": sf.get("title", "Security Finding"),
                "description": sf.get("description", ""),
                "cvss_score": sf.get("cvss_score", 5.0),
                "cvss_vector": sf.get("cvss_vector", "AV:N/AC:L/PR:N/UI:N/C:L/I:L/A:L"),
                "cwe_id": sf.get("cwe_id"),
                "details": sf.get("details"),
                "remediation": sf.get("remediation", ""),
            }
            all_findings.append(finding)

        # Calculate overall risk score using CVSS aggregation
        if all_findings:
            # Weight by severity
            severity_weights = {"critical": 4.0, "high": 2.0, "medium": 1.0, "low": 0.5, "info": 0.1}
            weighted_sum = sum(
                f["cvss_score"] * severity_weights.get(f["severity"], 1.0)
                for f in all_findings
            )
            total_weight = sum(severity_weights.get(f["severity"], 1.0) for f in all_findings)
            risk_score = round(weighted_sum / total_weight, 1) if total_weight > 0 else 0.0

            # Cap at 10.0
            risk_score = min(risk_score, 10.0)
        else:
            risk_score = 0.0

        # Add SDK vulnerabilities
        if sdk_info.get("vulnerable_sdks"):
            for vuln_sdk in sdk_info["vulnerable_sdks"]:
                all_findings.append({
                    "category": "third_party",
                    "severity": "high",
                    "title": f"Vulnerable SDK: {vuln_sdk['name']}",
                    "description": f"SDK {vuln_sdk['name']} version {vuln_sdk['version']} has known vulnerabilities",
                    "cvss_score": 7.5,
                    "cvss_vector": "AV:N/AC:L/PR:N/UI:N/C:H/I:H/A:H",
                    "cwe_id": "CWE-1104",  # Use of Unmaintained Third Party Component
                    "remediation": f"Update {vuln_sdk['name']} to latest version",
                })
                risk_score = max(risk_score, 7.5)

        return {
            "manifest": manifest,
            "sdk_count": sdk_info["count"],
            "sdk_info": sdk_info,
            "findings": all_findings,
            "risk_score": risk_score,
            "summary": {
                "critical": len([f for f in all_findings if f["severity"] == "critical"]),
                "high": len([f for f in all_findings if f["severity"] == "high"]),
                "medium": len([f for f in all_findings if f["severity"] == "medium"]),
                "low": len([f for f in all_findings if f["severity"] == "low"]),
                "info": len([f for f in all_findings if f["severity"] == "info"]),
            },
        }
