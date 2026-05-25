from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
import asyncio
import json
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

@router.websocket("/api/v1/alerts/stream")
async def alert_stream(ws: WebSocket):
    await ws.accept()
    try:
        # In production, this would subscribe to Kafka and push alerts
        # For now, send a test message every 10 seconds
        while True:
            test_alert = {
                "id": "test-001",
                "priority": "P1",
                "confidence": 0.75,
                "tool": "PentestGPT",
                "time": "2026-05-25T12:00:00Z",
                "message": "Test alert - WebSocket working"
            }
            await ws.send_json(test_alert)
            await asyncio.sleep(10)
    except WebSocketDisconnect:
        pass  # Client disconnected gracefully

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
