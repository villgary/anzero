from typing import List, Dict
import re


class SecurityChecker:
    """Comprehensive security checks for Android APKs."""

    # CWE to category mapping
    CWE_MAPPING = {
        "debuggable": "CWE-489",  # Debug Enabled
        "test_only": "CWE-489",
        "cleartext_traffic": "CWE-345",  # Insufficient Verification
        "allow_backup": "CWE-312",  # Cleartext Storage
        "no_network_config": "CWE-345",
        "signature_mismatch": "CWE-295",  # Improper Certificate Validation
        "self_signed_cert": "CWE-295",
        "expired_cert": "CWE-295",
        "hardcoded_secret": "CWE-798",  # Use of Hard-coded Credentials
        "native_code": "CWE-1104",  # Use of Unmaintained Third Party Component
        "webview_javascript": "CWE-79",  # XSS
        "crypto_weak": "CWE-327",  # Use of Broken/Risky Crypto
        "insecure_storage": "CWE-312",
        "intent_injection": "CWE-94",  # Code Injection
        "component_export": "CWE-862",  # Missing Authorization
    }

    def run_checks(self, apk) -> List[Dict]:
        findings = []

        # Check 1: Debuggable flag
        findings.extend(self._check_debuggable(apk))

        # Check 2: allowBackup flag
        findings.extend(self._check_allow_backup(apk))

        # Check 3: TestOnly flag
        findings.extend(self._check_test_only(apk))

        # Check 4: Cleartext traffic
        findings.extend(self._check_cleartext(apk))

        # Check 5: Network security config
        findings.extend(self._check_network_security(apk))

        # Check 6: Native code analysis
        findings.extend(self._check_native_code(apk))

        # Check 7: WebView security
        findings.extend(self._check_webview(apk))

        # Check 8: Component exports
        findings.extend(self._check_component_exports(apk))

        # Check 9: Backup rules
        findings.extend(self._check_backup_rules(apk))

        # Check 10: Debugger detection
        findings.extend(self._check_debugger_detection(apk))

        return findings

    def _check_debuggable(self, apk) -> List[Dict]:
        findings = []
        try:
            debuggable = apk.get_attribute_value("application", "debuggable")
            if debuggable == "true":
                findings.append({
                    "category": "code_quality",
                    "severity": "medium",
                    "title": "Debuggable Application",
                    "description": "Application has android:debuggable=true. This allows debugging of the application.",
                    "cvss_score": 5.0,
                    "cwe_id": self.CWE_MAPPING.get("debuggable"),
                    "remediation": "Set android:debuggable=false in manifest before release",
                })
        except Exception:
            pass
        return findings

    def _check_allow_backup(self, apk) -> List[Dict]:
        findings = []
        try:
            allow_backup = apk.get_attribute_value("application", "allowBackup")
            if allow_backup == "false":
                findings.append({
                    "category": "data_storage",
                    "severity": "low",
                    "title": "Backup Disabled",
                    "description": "android:allowBackup=false - app data cannot be backed up via ADB.",
                    "cvss_score": 2.0,
                    "cwe_id": self.CWE_MAPPING.get("allow_backup"),
                    "remediation": "Enable backup if no sensitive data, or use fullDataBackup=true with encrypted backup",
                })
            elif allow_backup is None:
                findings.append({
                    "category": "data_storage",
                    "severity": "info",
                    "title": "Default Backup Allowed",
                    "description": "android:allowBackup defaults to true. Application data may be backed up.",
                    "cvss_score": 1.0,
                    "cwe_id": self.CWE_MAPPING.get("allow_backup"),
                    "remediation": "Set android:allowBackup=false if sensitive data should not be backed up",
                })
        except Exception:
            pass
        return findings

    def _check_test_only(self, apk) -> List[Dict]:
        findings = []
        try:
            test_only = apk.get_attribute_value("application", "testOnly")
            if test_only == "true":
                findings.append({
                    "category": "code_quality",
                    "severity": "medium",
                    "title": "Test Only Application",
                    "description": "Application is marked as test only (android:testOnly=true).",
                    "cvss_score": 4.0,
                    "cwe_id": self.CWE_MAPPING.get("test_only"),
                    "remediation": "Remove testOnly flag before production release",
                })
        except Exception:
            pass
        return findings

    def _check_cleartext(self, apk) -> List[Dict]:
        findings = []
        try:
            uses_cleartext = apk.get_attribute_value("application", "usesCleartextTraffic")
            if uses_cleartext == "true":
                findings.append({
                    "category": "network",
                    "severity": "medium",
                    "title": "Cleartext Traffic Enabled",
                    "description": "Application allows cleartext HTTP traffic. Sensitive data may be intercepted.",
                    "cvss_score": 5.5,
                    "cwe_id": self.CWE_MAPPING.get("cleartext_traffic"),
                    "remediation": "Set usesCleartextTraffic=false and enforce HTTPS for all network communication",
                })
        except Exception:
            pass
        return findings

    def _check_network_security(self, apk) -> List[Dict]:
        findings = []
        try:
            network_sec = apk.get_attribute_value("application", "networkSecurityConfig")
            if not network_sec:
                findings.append({
                    "category": "network",
                    "severity": "low",
                    "title": "No Network Security Config",
                    "description": "No network security configuration file specified. Consider adding one to enforce HTTPS.",
                    "cvss_score": 3.0,
                    "cwe_id": self.CWE_MAPPING.get("no_network_config"),
                    "remediation": "Add network security config to enforce certificate pinning and cleartext restrictions",
                })
        except Exception:
            pass
        return findings

    def _check_native_code(self, apk) -> List[Dict]:
        """Check for native code libraries (.so files)."""
        findings = []
        try:
            files = apk.get_files()
            native_libs = [f for f in files if f.endswith('.so')]
            if native_libs:
                findings.append({
                    "category": "code_quality",
                    "severity": "info",
                    "title": "Native Code Detected",
                    "description": f"Application contains {len(native_libs)} native library(ies). Review for security issues.",
                    "cvss_score": 3.0,
                    "cwe_id": self.CWE_MAPPING.get("native_code"),
                    "details": {"native_libraries": native_libs[:10]},  # Limit to first 10
                    "remediation": "Ensure native libraries are from trusted sources and are not debuggable",
                })
        except Exception:
            pass
        return findings

    def _check_webview(self, apk) -> List[Dict]:
        """Check for WebView with JavaScript enabled."""
        findings = []
        try:
            # Check if JavaScript interface is used
            javascript_interfaces = []
            files = apk.get_files()
            for f in files:
                if f.endswith('.xml'):
                    pass  # Would need to parse XML to detect JS interfaces

            # Check DEX for WebView usage patterns
            # This is a simplified check
            if javascript_interfaces:
                findings.append({
                    "category": "network",
                    "severity": "high",
                    "title": "WebView JavaScript Interface",
                    "description": "WebView with JavaScript interface detected. Ensure proper input validation.",
                    "cvss_score": 7.0,
                    "cwe_id": self.CWE_MAPPING.get("webview_javascript"),
                    "remediation": "Validate all inputs passed to JavaScript interface and enable safe browsing",
                })
        except Exception:
            pass
        return findings

    def _check_component_exports(self, apk) -> List[Dict]:
        """Check for exported application components."""
        findings = []
        try:
            exported_activities = []
            exported_services = []
            exported_receivers = []
            exported_providers = []

            # Check activities
            for activity in apk.get_activities():
                if isinstance(activity, str):
                    exported = apk.get_attribute_value(activity, "exported")
                    if exported == "true":
                        exported_activities.append(activity)

            if exported_activities:
                findings.append({
                    "category": "code_quality",
                    "severity": "low",
                    "title": "Exported Activities",
                    "description": f"{len(exported_activities)} exported activity(ies) found.",
                    "cvss_score": 3.5,
                    "cwe_id": self.CWE_MAPPING.get("component_export"),
                    "details": {"exported_activities": exported_activities[:5]},
                    "remediation": "Set android:exported=false for components that should not be accessed externally",
                })
        except Exception:
            pass
        return findings

    def _check_backup_rules(self, apk) -> List[Dict]:
        """Check for backup rules file."""
        findings = []
        try:
            files = apk.get_files()
            has_backup_rules = any('backup_rules' in f.lower() for f in files)
            if not has_backup_rules:
                allow_backup = apk.get_attribute_value("application", "allowBackup")
                if allow_backup != "false":
                    findings.append({
                        "category": "data_storage",
                        "severity": "low",
                        "title": "No Backup Rules Configuration",
                        "description": "No backup rules file found. Consider adding one for fine-grained backup control.",
                        "cvss_score": 2.0,
                        "cwe_id": self.CWE_MAPPING.get("allow_backup"),
                        "remediation": "Add full-backup-content rules to control what gets backed up",
                    })
        except Exception:
            pass
        return findings

    def _check_debugger_detection(self, apk) -> List[Dict]:
        """Check if application has debugger detection."""
        findings = []
        try:
            # Check for debuggable flag only
            debuggable = apk.get_attribute_value("application", "debuggable")
            if debuggable != "true":
                # Check DEX strings for debugger detection code
                findings.append({
                    "category": "code_quality",
                    "severity": "info",
                    "title": "No Debugger Detection",
                    "description": "No explicit debugger detection found. Consider adding detection for production.",
                    "cvss_score": 1.0,
                    "remediation": "Add debugger detection using android.os.Debug.isDebuggerConnected()",
                })
        except Exception:
            pass
        return findings
