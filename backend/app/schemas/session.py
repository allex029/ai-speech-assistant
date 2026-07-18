"""Session and fluency schemas."""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.chat import ConversationRead
from app.schemas.speech import TranscriptRead


class SessionStartRequest(BaseModel):
    user_id: Optional[str] = None
    title: Optional[str] = Field(default=None, max_length=255)
    meta: Optional[dict[str, Any]] = None


class SessionStartResponse(BaseModel):
    id: str
    status: str
    started_at: datetime
    title: Optional[str] = None


class SessionEndRequest(BaseModel):
    session_id: str


class SessionEndResponse(BaseModel):
    id: str
    status: str
    started_at: datetime
    ended_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None


class FluencyAnalyzeRequest(BaseModel):
    transcript: str = Field(..., min_length=1)
    timestamps: list[dict[str, Any]] = Field(default_factory=list)
    session_id: Optional[str] = None
    transcript_id: Optional[str] = None


class FluencyAnalyzeResponse(BaseModel):
    words_per_minute: float
    filler_words: list[str]
    pause_count: int
    longest_pause: float
    average_pause: float
    fluency_score: float
    # Extra fields useful for the Practice UI / future ML swap-in
    total_words: int = 0
    speech_duration: float = 0.0
    filler_word_count: int = 0


class FluencyMetricsRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    session_id: Optional[str] = None
    words_per_minute: float
    filler_words: list[Any]
    pause_count: int
    longest_pause: float
    average_pause: float
    fluency_score: float
    created_at: Optional[datetime] = None


class SessionDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: Optional[str] = None
    status: str
    title: Optional[str] = None
    started_at: datetime
    ended_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    meta: Optional[dict[str, Any]] = None
    transcripts: list[TranscriptRead] = Field(default_factory=list)
    fluency_metrics: list[FluencyMetricsRead] = Field(default_factory=list)
    conversations: list[ConversationRead] = Field(default_factory=list)
