from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User, ScanJob, ScanStatusEnum, ScanResult
from app.api.deps import get_current_user

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/overview")
def get_stats_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Get scan counts
    total = db.query(ScanJob).filter(ScanJob.user_id == current_user.id).count()
    completed = db.query(ScanJob).filter(
        ScanJob.user_id == current_user.id,
        ScanJob.status == ScanStatusEnum.COMPLETED
    ).count()
    pending = db.query(ScanJob).filter(
        ScanJob.user_id == current_user.id,
        ScanJob.status.in_([ScanStatusEnum.PENDING, ScanStatusEnum.SCANNING])
    ).count()

    # Get severity breakdown from scan results
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
