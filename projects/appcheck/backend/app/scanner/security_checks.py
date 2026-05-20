from typing import List, Dict


class SecurityChecker:
    def run_checks(self, apk) -> List[Dict]:
        findings = []

        # Check 1: Debuggable flag
        try:
            debuggable = apk.get_attribute_value("application", "debuggable")
            if debuggable == "true":
                findings.append({
                    "category": "code_quality",
                    "severity": "medium",
                    "title": "Debuggable Application",
                    "description": "Application has android:debuggable=true",
                    "cvss_score": 5.0,
                    "remediation": "Set android:debuggable=false in manifest",
                })
        except Exception:
            pass

        # Check 2: allowBackup flag
        try:
            allow_backup = apk.get_attribute_value("application", "allowBackup")
            if allow_backup == "false":
                findings.append({
                    "category": "data_storage",
                    "severity": "low",
                    "title": "Backup Disabled",
                    "description": "android:allowBackup=false - app data cannot be backed up",
                    "cvss_score": 2.0,
                    "remediation": "Consider enabling backup if no sensitive data",
                })
        except Exception:
            pass

        # Check 3: TestOnly flag
        try:
            test_only = apk.get_attribute_value("application", "testOnly")
            if test_only == "true":
                findings.append({
                    "category": "code_quality",
                    "severity": "medium",
                    "title": "Test Only Application",
                    "description": "Application is marked as test only",
                    "cvss_score": 4.0,
                    "remediation": "Remove testOnly flag before production",
                })
        except Exception:
            pass

        # Check 4: Cleartext traffic
        try:
            uses_cleartext = apk.get_attribute_value("application", "usesCleartextTraffic")
            if uses_cleartext == "true":
                findings.append({
                    "category": "network",
                    "severity": "medium",
                    "title": "Cleartext Traffic Enabled",
                    "description": "Application allows cleartext HTTP traffic",
                    "cvss_score": 5.5,
                    "remediation": "Set usesCleartextTraffic=false and use HTTPS",
                })
        except Exception:
            pass

        # Check 5: Network security config
        try:
            network_sec = apk.get_attribute_value("application", "networkSecurityConfig")
            if not network_sec:
                findings.append({
                    "category": "network",
                    "severity": "low",
                    "title": "No Network Security Config",
                    "description": "No network security configuration file specified",
                    "cvss_score": 3.0,
                    "remediation": "Consider adding a network security config to enforce HTTPS",
                })
        except Exception:
            pass

        return findings
