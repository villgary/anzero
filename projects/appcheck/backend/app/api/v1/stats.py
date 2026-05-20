from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.api.deps import get_current_user

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/overview")
def get_stats_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return {"total_scans": 0, "completed": 0, "pending": 0}
