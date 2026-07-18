"""Speech / transcription schemas."""

from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class WordTimestamp(BaseModel):
    word: str
    start: float
    end: float


class TranscribeResponse(BaseModel):
    """Response for POST /api/speech/transcribe."""

    transcript: str
    timestamps: list[WordTimestamp] = Field(default_factory=list)
    duration: float = 0.0
    # Reserved for future pronunciation scoring
    pronunciation_data: Optional[dict[str, Any]] = None
    language: Optional[str] = None
    model_used: Optional[str] = None


class TranscriptRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    session_id: Optional[str] = None
    text: str
    duration: Optional[float] = None
    timestamps: Optional[list[dict[str, Any]]] = None
    created_at: Any = None
