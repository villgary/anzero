from typing import List, Dict


class SecurityChecker:
    def run_checks(self, analysis) -> List[Dict]:
        findings = []

        apk = analysis.get_apk()

        # Check 1: Debuggable flag
        if apk.is_debuggable():
            findings.append({
                "category": "code_quality",
                "severity": "medium",
                "title": "Debuggable Application",
                "description": "Application has android:debuggable=true",
                "cvss_score": 5.0,
                "remediation": "Set android:debuggable=false in manifest",
            })

        # Check 2: allowBackup flag (need to check manifest)
        try:
            manifest = apk.get_android_manifest_xml()
            if manifest is not None:
                app_elem = manifest.find("application")
                if app_elem is not None:
                    allow_backup = app_elem.get("{http://schemas.android.com/apk/res/android}allowBackup")
                    if allow_backup is None or allow_backup.lower() != "false":
                        pass  # default is true, which is potentially risky
                    else:
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
            test_only = apk.get_attribute("application", "testOnly")
            if test_only:
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
            uses_cleartext = apk.get_attribute("application", "usesCleartextTraffic")
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
            network_sec = apk.get_attribute("application", "networkSecurityConfig")
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
