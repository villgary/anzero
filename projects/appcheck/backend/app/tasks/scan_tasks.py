import os
from datetime import datetime
from app.celery_app import celery_app
from app.database import SessionLocal
from app.models.user import ScanJob, ScanStatusEnum, PlatformEnum, ScanResult, SeverityEnum
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
