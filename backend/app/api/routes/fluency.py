"""Fluency analysis routes."""

from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.database.database import get_database
from app.schemas.session import FluencyAnalyzeRequest, FluencyAnalyzeResponse
from app.services.fluency_service import FluencyService, get_fluency_service
from app.services.session_service import SessionService

router = APIRouter(prefix="/fluency", tags=["fluency"])


@router.post("/analyze", response_model=FluencyAnalyzeResponse)
async def analyze_fluency(
    payload: FluencyAnalyzeRequest,
    fluency: FluencyService = Depends(get_fluency_service),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> FluencyAnalyzeResponse:
    """
    Analyze speaking fluency from transcript + word timestamps.

    Uses placeholder heuristics today; FluencyService is designed so
    an ML model can replace the analyzer without changing this route.
    """
    result = fluency.analyze(payload.transcript, payload.timestamps)

    if payload.session_id:
        session_service = SessionService(db)
        await session_service.save_fluency_metrics(
            metrics=result.model_dump(),
            session_id=payload.session_id,
            transcript_id=payload.transcript_id,
        )

    return result
