from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.detection_engine.d25.fusion_engine import FusionEngine

router = APIRouter()
fusion_engine = FusionEngine()

@router.get("/health")
async def health_check():
    return {"status": "ok", "version": "0.1.0"}

@router.get("/api/v1/dashboard/stats")
async def get_dashboard_stats(db: Session = Depends(get_db)):
    return {
        "attackCount": 127,
        "mttd": "2.3min",
        "counterRate": 94.5,
        "threatLevel": "高"
    }

@router.post("/api/v1/detect")
async def detect_event(event: dict, db: Session = Depends(get_db)):
    signals = event.get("signals", [])
    context = event.get("context", {})
    result = fusion_engine.score(signals, context)
    return {"confidence": result.score, "level": result.level}
