"""Speech transcription routes."""

from typing import Optional

from fastapi import APIRouter, Depends, File, Form, UploadFile
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.database.database import get_database
from app.schemas.speech import TranscribeResponse
from app.services.session_service import SessionService
from app.services.whisper_service import WhisperService, get_whisper_service
from app.utils.audio import read_and_validate_audio

router = APIRouter(prefix="/speech", tags=["speech"])


@router.post("/transcribe", response_model=TranscribeResponse)
async def transcribe_audio(
    file: UploadFile = File(..., description="Audio file to transcribe"),
    session_id: Optional[str] = Form(default=None),
    language: Optional[str] = Form(default="en"),
    whisper: WhisperService = Depends(get_whisper_service),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> TranscribeResponse:
    """
    Transcribe an audio upload via Groq Whisper Large V3 Turbo.

    Returns transcript, word-level timestamps, and duration.
    Pronunciation data will be added in a future release.
    """
    audio_bytes = await read_and_validate_audio(file)
    result = await whisper.transcribe(
        audio_bytes,
        filename=file.filename or "audio.webm",
        language=language,
    )

    if session_id:
        session_service = SessionService(db)
        await session_service.save_transcript(
            text=result.transcript,
            session_id=session_id,
            duration=result.duration,
            timestamps=[t.model_dump() for t in result.timestamps],
            language=result.language,
            model_used=result.model_used,
            audio_filename=file.filename,
        )

    return result
