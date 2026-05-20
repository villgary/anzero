import os
import hashlib
import uuid
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User, ScanJob, ScanStatusEnum, PlatformEnum
from app.api.deps import get_current_user
from app.config import settings

router = APIRouter(prefix="/scans", tags=["scans"])


ALLOWED_EXTENSIONS = {
    "android": [".apk"],
    "ios": [".ipa"],
    "harmony": [".hap"]
}


def get_platform_from_filename(filename: str) -> Optional[PlatformEnum]:
    ext = os.path.splitext(filename.lower())[1]
    for platform, extensions in ALLOWED_EXTENSIONS.items():
        if ext in extensions:
            return PlatformEnum[platform.upper()]
    return None


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    app_name: str = Query(..., description="Application name"),
    app_version: Optional[str] = Query(None, description="Application version"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Validate file extension
    platform = get_platform_from_filename(file.filename)
    if not platform:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type. Allowed: {ALLOWED_EXTENSIONS}"
        )

    # Create upload directory if not exists
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    # Generate unique filename
    file_ext = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)

    # Save file
    content = await file.read()
    if len(content) > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Max size: {settings.MAX_FILE_SIZE} bytes"
        )

    with open(file_path, "wb") as f:
        f.write(content)

    # Calculate MD5
    md5_hash = hashlib.md5(content).hexdigest()

    # Create scan job
    scan_job = ScanJob(
        user_id=current_user.id,
        app_name=app_name,
        app_version=app_version,
        platform=platform,
        file_path=file_path,
        file_size=len(content),
        file_md5=md5_hash,
        status=ScanStatusEnum.PENDING
    )
    db.add(scan_job)
    db.commit()
    db.refresh(scan_job)

    return {
        "id": str(scan_job.id),
        "app_name": scan_job.app_name,
        "platform": scan_job.platform.value,
        "file_size": scan_job.file_size,
        "file_md5": scan_job.file_md5,
        "status": scan_job.status.value
    }


@router.get("")
def list_scans(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    platform: Optional[PlatformEnum] = None,
    status_filter: Optional[ScanStatusEnum] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(ScanJob).filter(ScanJob.user_id == current_user.id)
    if platform:
        query = query.filter(ScanJob.platform == platform)
    if status_filter:
        query = query.filter(ScanJob.status == status_filter)

    total = query.count()
    jobs = query.order_by(ScanJob.created_at.desc()).offset(skip).limit(limit).all()

    return {
        "total": total,
        "items": [
            {
                "id": str(job.id),
                "app_name": job.app_name,
                "app_version": job.app_version,
                "platform": job.platform.value,
                "file_size": job.file_size,
                "file_md5": job.file_md5,
                "status": job.status.value,
                "risk_score": float(job.risk_score) if job.risk_score else None,
                "created_at": job.created_at.isoformat() if job.created_at else None,
                "completed_at": job.completed_at.isoformat() if job.completed_at else None,
            }
            for job in jobs
        ]
    }


@router.get("/{scan_id}")
def get_scan(
    scan_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    job = db.query(ScanJob).filter(
        ScanJob.id == scan_id,
        ScanJob.user_id == current_user.id
    ).first()
    if not job:
        raise HTTPException(status_code=404, detail="Scan not found")

    return {
        "id": str(job.id),
        "app_name": job.app_name,
        "app_version": job.app_version,
        "platform": job.platform.value,
        "file_size": job.file_size,
        "file_md5": job.file_md5,
        "status": job.status.value,
        "risk_score": float(job.risk_score) if job.risk_score else None,
        "sdk_count": job.sdk_count,
        "error_message": job.error_message,
        "created_at": job.created_at.isoformat() if job.created_at else None,
        "started_at": job.started_at.isoformat() if job.started_at else None,
        "completed_at": job.completed_at.isoformat() if job.completed_at else None,
    }


@router.delete("/{scan_id}")
def delete_scan(
    scan_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    job = db.query(ScanJob).filter(
        ScanJob.id == scan_id,
        ScanJob.user_id == current_user.id
    ).first()
    if not job:
        raise HTTPException(status_code=404, detail="Scan not found")

    # Delete file
    if os.path.exists(job.file_path):
        os.remove(job.file_path)

    db.delete(job)
    db.commit()

    return {"message": "Scan deleted"}