from typing import Dict, List

DANGEROUS_PERMISSIONS = {
    "android.permission.READ_SMS": ("high", "Can read SMS messages"),
    "android.permission.SEND_SMS": ("high", "Can send SMS messages"),
    "android.permission.READ_CONTACTS": ("high", "Can read contacts"),
    "android.permission.WRITE_CONTACTS": ("medium", "Can write contacts"),
    "android.permission.RECORD_AUDIO": ("high", "Can record audio"),
    "android.permission.CAMERA": ("high", "Can access camera"),
    "android.permission.ACCESS_FINE_LOCATION": ("high", "Can access precise location"),
    "android.permission.ACCESS_COARSE_LOCATION": ("medium", "Can access approximate location"),
    "android.permission.READ_EXTERNAL_STORAGE": ("medium", "Can read external storage"),
    "android.permission.WRITE_EXTERNAL_STORAGE": ("medium", "Can write external storage"),
    "android.permission.READ_CALL_LOG": ("critical", "Can read call log"),
    "android.permission.WRITE_CALL_LOG": ("critical", "Can write call log"),
    "android.permission.PROCESS_OUTGOING_CALLS": ("critical", "Can process outgoing calls"),
}


class PermissionAnalyzer:
    def analyze(self, permissions: List[str]) -> List[Dict]:
        findings = []
        for perm in permissions:
            if perm in DANGEROUS_PERMISSIONS:
                severity, description = DANGEROUS_PERMISSIONS[perm]
                findings.append({
                    "permission": perm,
                    "severity": severity,
                    "description": description,
                })
        return findings
