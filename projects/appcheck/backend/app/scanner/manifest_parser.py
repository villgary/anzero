from typing import Dict


class ManifestParser:
    def parse(self, analysis) -> Dict:
        apk = analysis.get_apk()

        return {
            "package_name": apk.get_package(),
            "version_name": apk.get_androidver(),
            "version_code": apk.get_androidversion_code(),
            "min_sdk": apk.get_min_sdk_version(),
            "target_sdk": apk.get_target_sdk_version(),
            "permissions": apk.get_permissions(),
            "activities": [a.getName() for a in apk.get_activities()],
            "services": [s.getName() for s in apk.get_services()],
            "receivers": [r.getName() for r in apk.get_receivers()],
            "providers": [p.getName() for p in apk.get_providers()],
        }
