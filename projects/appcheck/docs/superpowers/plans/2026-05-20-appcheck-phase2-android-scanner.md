# AppScan Pro - Phase 2 Android Scanner Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement Android APK static scanning with manifest analysis, permission analysis, and basic security checks.

**Architecture:** Celery async task for APK analysis, results stored in scan_results table with CVSS scoring.

**Tech Stack:** Androguard for APK parsing, celery worker for async processing, CVSS 3.1 for scoring.

---

## File Structure

```
backend/
├── app/
│   ├── scanner/                    # New: Scanner module
│   │   ├── __init__.py
│   │   ├── android_scanner.py      # Main APK analysis logic
│   │   ├── manifest_parser.py      # AndroidManifest.xml parsing
│   │   ├── permission_analyzer.py  # Permission analysis
│   │   ├── security_checks.py      # Security detection rules
│   │   ├── sdk_detector.py         # Third-party SDK detection
│   │   └── cvss_scorer.py         # CVSS 3.1 scoring
│   ├── tasks/                      # New: Celery tasks
│   │   ├── __init__.py
│   │   └── scan_tasks.py          # Async scan job tasks
│   └── api/v1/scans.py            # Modify: Add scan trigger endpoint
├── requirements.txt               # Modify: Add androguard
└── migrations/                    # Auto-generated
```

---

## Tasks

### Task 1: Add APK Analysis Dependencies

**Files:**
- Modify: `backend/requirements.txt`
- Modify: `backend/app/config.py`

- [ ] **Step 1: Add dependencies to requirements.txt**

```
# Add to requirements.txt
androguard==3.3.5
celery[redis]==5.3.6
```

- [ ] **Step 2: Rebuild backend container**

```bash
docker-compose build backend
docker-compose up -d
```

- [ ] **Step 3: Verify androguard installed**

```bash
docker-compose exec backend python -c "import androguard; print(androguard.__version__)"
```

---

### Task 2: Create Android Scanner Module

**Files:**
- Create: `backend/app/scanner/__init__.py`
- Create: `backend/app/scanner/android_scanner.py`
- Create: `backend/app/scanner/manifest_parser.py`
- Create: `backend/app/scanner/permission_analyzer.py`
- Create: `backend/app/scanner/security_checks.py`
- Create: `backend/app/scanner/sdk_detector.py`
- Create: `backend/app/scanner/cvss_scorer.py`

- [ ] **Step 1: Create scanner module __init__.py**

```python
from .android_scanner import AndroidScanner

__all__ = ["AndroidScanner"]
```

- [ ] **Step 2: Create CVSS scorer (shared utility)**

```python
# backend/app/scanner/cvss_scorer.py
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
```

- [ ] **Step 3: Create permission analyzer**

```python
# backend/app/scanner/permission_analyzer.py
from typing import Dict, List, Tuple

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
```

- [ ] **Step 4: Create manifest parser**

```python
# backend/app/scanner/manifest_parser.py
from typing import Dict, List, Optional
from androguard.core.analysis.analysis import Analysis

class ManifestParser:
    def parse(self, analysis: Analysis) -> Dict:
        apk = analysis.get_apk()
        manifest = apk.get_android_manifest_xml()

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
```

- [ ] **Step 5: Create security checks**

```python
# backend/app/scanner/security_checks.py
from typing import List, Dict

class SecurityChecker:
    def run_checks(self, analysis) -> List[Dict]:
        findings = []

        # Check 1: Debuggable flag
        if analysis.get_apk().is_debuggable():
            findings.append({
                "category": "code_quality",
                "severity": "medium",
                "title": "Debuggable Application",
                "description": "Application has android:debuggable=true",
                "cvss_score": 5.0,
                "remediation": "Set android:debuggable=false in manifest",
            })

        # Check 2: AllowBackup flag
        if not analysis.get_apk().get_attribute("application", "allowBackup"):
            findings.append({
                "category": "data_storage",
                "severity": "low",
                "title": "Backup Disabled",
                "description": "android:allowBackup=false - app data cannot be backed up",
                "cvss_score": 2.0,
                "remediation": "Consider enabling backup if no sensitive data",
            })

        # Check 3: TestOnly flag
        if analysis.get_apk().get_attribute("application", "testOnly"):
            findings.append({
                "category": "code_quality",
                "severity": "medium",
                "title": "Test Only Application",
                "description": "Application is marked as test only",
                "cvss_score": 4.0,
                "remediation": "Remove testOnly flag before production",
            })

        return findings
```

- [ ] **Step 6: Create SDK detector**

```python
# backend/app/scanner/sdk_detector.py
from typing import List, Dict, Set

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
    }

    def detect(self, analysis) -> Dict:
        classes = set()
        for dvm in analysis.get_dex().get_classes():
            classes.add(dvm.get_name())

        detected = []
        for package, name in self.KNOWN_SDKS.items():
            if any(package in c for c in classes):
                detected.append({"package": package, "name": name})

        return {
            "count": len(detected),
            "sdks": detected,
        }
```

- [ ] **Step 7: Create main Android scanner**

```python
# backend/app/scanner/android_scanner.py
from typing import Dict, List
from androguard.core.analysis.analysis import Analysis
from androguard import AnalyzeAPK
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
```

---

### Task 3: Create Celery Tasks for Async Scanning

**Files:**
- Create: `backend/app/tasks/__init__.py`
- Create: `backend/app/tasks/scan_tasks.py`
- Create: `backend/app/celery_app.py`
- Modify: `backend/app/config.py`

- [ ] **Step 1: Create Celery app configuration**

```python
# backend/app/celery_app.py
from celery import Celery
from app.config import settings

celery_app = Celery(
    "appcheck",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.tasks.scan_tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)
```

- [ ] **Step 2: Create scan task**

```python
# backend/app/tasks/scan_tasks.py
import os
from datetime import datetime
from app.celery_app import celery_app
from app.database import SessionLocal
from app.models.user import ScanJob, ScanStatusEnum, PlatformEnum
from app.scanner.android_scanner import AndroidScanner
from app.scanner.cvss_scorer import CVSSScorer

@celery_app.task(bind=True)
def scan_apk(self, scan_job_id: str):
    """Async APK scanning task."""
    db = SessionLocal()
    try:
        # Update job status to scanning
        job = db.query(ScanJob).filter(ScanJob.id == scan_job_id).first()
        if not job:
            return {"error": "Scan job not found"}

        job.status = ScanStatusEnum.SCANNING
        job.started_at = datetime.utcnow()
        db.commit()

        # Run scanner
        scanner = AndroidScanner(job.file_path)
        result = scanner.scan()

        # Store findings
        from app.models.user import ScanResult, SeverityEnum
        for finding in result["findings"]:
            severity = CVSSScorer.get_severity(finding["cvss_score"])
            scan_result = ScanResult(
                job_id=job.id,
                category=finding["category"],
                severity=SeverityEnum[severity.upper()],
                cvss_score=finding["cvss_score"],
                title=finding["title"],
                description=finding.get("description", ""),
                remediation=finding.get("remediation", ""),
            )
            db.add(scan_result)

        # Update job
        job.status = ScanStatusEnum.COMPLETED
        job.risk_score = result["risk_score"]
        job.sdk_count = result["sdk_count"]
        job.completed_at = datetime.utcnow()
        db.commit()

        return {"status": "completed", "risk_score": result["risk_score"]}

    except Exception as e:
        job.status = ScanStatusEnum.FAILED
        job.error_message = str(e)
        db.commit()
        return {"error": str(e)}
    finally:
        db.close()
```

- [ ] **Step 3: Modify scans.py to trigger Celery task**

Add to `backend/app/api/v1/scans.py`:
```python
from app.tasks.scan_tasks import scan_apk

# In upload_file function, after creating scan_job:
# Trigger async scan for Android
if platform == PlatformEnum.ANDROID:
    scan_apk.delay(str(scan_job.id))
```

---

### Task 4: Update Stats API to Return Scan Results

**Files:**
- Modify: `backend/app/api/v1/stats.py`

- [ ] **Step 1: Update stats overview**

```python
# Modify stats/overview to include scan results summary
@router.get("/overview")
def get_overview(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Existing code plus:
    # Count findings by severity
    results = db.query(ScanResult).join(ScanJob).filter(
        ScanJob.user_id == current_user.id
    ).all()

    severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
    for r in results:
        severity_counts[r.severity.value] += 1

    return {
        "total_scans": total,
        "completed": completed,
        "pending": pending,
        "severity_breakdown": severity_counts,
    }
```

---

### Task 5: Add API Endpoint to Get Scan Results

**Files:**
- Modify: `backend/app/api/v1/scans.py`

- [ ] **Step 1: Add endpoint for scan results**

```python
@router.get("/{scan_id}/results")
def get_scan_results(
    scan_id: uuid.UUID,
    severity: Optional[SeverityEnum] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    job = db.query(ScanJob).filter(
        ScanJob.id == scan_id,
        ScanJob.user_id == current_user.id
    ).first()
    if not job:
        raise HTTPException(status_code=404, detail="Scan not found")

    query = db.query(ScanResult).filter(ScanResult.job_id == scan_id)
    if severity:
        query = query.filter(ScanResult.severity == severity)

    results = query.all()

    return {
        "scan_id": str(scan_id),
        "risk_score": float(job.risk_score) if job.risk_score else None,
        "total_findings": len(results),
        "findings": [
            {
                "id": str(r.id),
                "category": r.category,
                "severity": r.severity.value,
                "cvss_score": float(r.cvss_score) if r.cvss_score else None,
                "cwe_id": r.cwe_id,
                "title": r.title,
                "description": r.description,
                "remediation": r.remediation,
            }
            for r in results
        ]
    }
```

---

### Task 6: Run Database Migration

- [ ] **Step 1: Generate migration for new tables**

```bash
docker-compose exec backend alembic revision --autogenerate -m "add scan results table"
```

- [ ] **Step 2: Apply migration**

```bash
docker-compose exec backend alembic upgrade head
```

- [ ] **Step 3: Verify tables created**

```bash
docker-compose exec db psql -U appcheck -d appcheck -c "\dt"
```

---

## Verification

After all tasks complete:

1. **Upload an APK file** via API
2. **Check scan results** via GET /api/v1/scans/{id}/results
3. **Verify findings** include permissions, security checks
4. **Verify risk score** is calculated correctly
