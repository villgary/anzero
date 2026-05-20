from typing import Dict, List, Set


class SDKDetector:
    KNOWN_SDKS = {
        "com.facebook": "Facebook SDK",
        "com.google.android.gms": "Google Play Services",
        "com.google.firebase": "Firebase",
        "com.twitter": "Twitter SDK",
        "com.alipay": "Alipay SDK",
        "com.tencent": "Tencent SDK",
        "com.bumptech.glide": "Glide",
        "com.squareup.okhttp": "OkHttp",
        "com.squareup.retrofit": "Retrofit",
        "io.reactivex": "RxJava",
        "org.jetbrains": "JetBrains",
        "com.crashlytics": "Crashlytics",
        "com.google.code.gson": "Gson",
        "com.fasterxml.jackson": "Jackson",
    }

    def detect(self, analysis) -> Dict:
        detected = []

        try:
            for dvm in analysis.get_dex().get_classes():
                class_name = dvm.get_name()
                for package, name in self.KNOWN_SDKS.items():
                    if package.lower() in class_name.lower():
                        detected.append({"package": package, "name": name})
        except Exception:
            pass

        # Remove duplicates
        seen = set()
        unique = []
        for sdk in detected:
            if sdk["package"] not in seen:
                seen.add(sdk["package"])
                unique.append(sdk)

        return {
            "count": len(unique),
            "sdks": unique,
        }
