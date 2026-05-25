from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.detection_engine.d25.fusion_engine import FusionEngine

router = APIRouter()
fusion_engine = FusionEngine()


class DetectRequest(BaseModel):
    signals: list[float]
    context: dict


class DetectResponse(BaseModel):
    confidence: float
    level: str

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

@router.post("/api/v1/detect", response_model=DetectResponse)
async def detect_event(request: DetectRequest, db: Session = Depends(get_db)):
    try:
        result = fusion_engine.score(request.signals, request.context)
        return DetectResponse(confidence=result.score, level=result.level)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
