"""Practice session lifecycle routes."""

from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.database.database import get_database
from app.schemas.session import (
    SessionDetailResponse,
    SessionEndRequest,
    SessionEndResponse,
    SessionStartRequest,
    SessionStartResponse,
)
from app.services.session_service import SessionService

router = APIRouter(prefix="/session", tags=["session"])


@router.post("/start", response_model=SessionStartResponse)
async def start_session(
    payload: SessionStartRequest | None = None,
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> SessionStartResponse:
    """Start a new speaking practice session."""
    body = payload or SessionStartRequest()
    service = SessionService(db)
    session = await service.start_session(
        user_id=body.user_id,
        title=body.title,
        meta=body.meta,
    )
    return SessionStartResponse(
        id=session["id"],
        status=session["status"],
        started_at=session["started_at"],
        title=session["title"],
    )


@router.post("/end", response_model=SessionEndResponse)
async def end_session(
    payload: SessionEndRequest,
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> SessionEndResponse:
    """End an active practice session and record duration."""
    service = SessionService(db)
    session = await service.end_session(payload.session_id)
    return SessionEndResponse(
        id=session["id"],
        status=session["status"],
        started_at=session["started_at"],
        ended_at=session["ended_at"],
        duration_seconds=session["duration_seconds"],
    )


@router.get("/{session_id}", response_model=SessionDetailResponse)
async def get_session(
    session_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> SessionDetailResponse:
    """Fetch a session with transcripts, fluency metrics, and conversations."""
    service = SessionService(db)
    session = await service.get_session(session_id, with_relations=True)
    return SessionDetailResponse(**session)
