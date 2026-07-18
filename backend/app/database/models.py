"""SQLAlchemy ORM models for SpeakFlow."""

from datetime import datetime
from typing import Any, Optional
from uuid import uuid4

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import ConversationRole, SessionStatus
from app.database.database import Base


def _uuid() -> str:
    return str(uuid4())


class User(Base):
    """Registered or anonymous learner."""

    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=_uuid
    )
    email: Mapped[Optional[str]] = mapped_column(
        String(255), unique=True, index=True, nullable=True
    )
    username: Mapped[Optional[str]] = mapped_column(
        String(100), unique=True, index=True, nullable=True
    )
    hashed_password: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True
    )
    display_name: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    is_anonymous: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    sessions: Mapped[list["PracticeSession"]] = relationship(
        "PracticeSession",
        back_populates="user",
        cascade="all, delete-orphan",
    )


class PracticeSession(Base):
    """A single speaking practice session."""

    __tablename__ = "sessions"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=_uuid
    )
    user_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    status: Mapped[str] = mapped_column(
        String(32), default=SessionStatus.ACTIVE.value, index=True
    )
    title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    ended_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    duration_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    meta: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    user: Mapped[Optional["User"]] = relationship("User", back_populates="sessions")
    transcripts: Mapped[list["Transcript"]] = relationship(
        "Transcript",
        back_populates="session",
        cascade="all, delete-orphan",
    )
    fluency_metrics: Mapped[list["FluencyMetrics"]] = relationship(
        "FluencyMetrics",
        back_populates="session",
        cascade="all, delete-orphan",
    )
    conversations: Mapped[list["Conversation"]] = relationship(
        "Conversation",
        back_populates="session",
        cascade="all, delete-orphan",
    )


class Transcript(Base):
    """Speech-to-text result for a turn within a session."""

    __tablename__ = "transcripts"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=_uuid
    )
    session_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("sessions.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    text: Mapped[str] = mapped_column(Text, nullable=False)
    language: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)
    duration: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    # Word-level timestamps from Whisper: [{word, start, end}, ...]
    timestamps: Mapped[Optional[list[dict[str, Any]]]] = mapped_column(
        JSONB, nullable=True
    )
    # Reserved for future pronunciation scoring payloads
    pronunciation_data: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSONB, nullable=True
    )
    audio_filename: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    model_used: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    session: Mapped[Optional["PracticeSession"]] = relationship(
        "PracticeSession", back_populates="transcripts"
    )


class FluencyMetrics(Base):
    """Computed fluency analytics for a transcript or session turn."""

    __tablename__ = "fluency_metrics"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=_uuid
    )
    session_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("sessions.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    transcript_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("transcripts.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    words_per_minute: Mapped[float] = mapped_column(Float, default=0.0)
    filler_words: Mapped[list[Any]] = mapped_column(JSONB, default=list)
    filler_word_count: Mapped[int] = mapped_column(Integer, default=0)
    pause_count: Mapped[int] = mapped_column(Integer, default=0)
    longest_pause: Mapped[float] = mapped_column(Float, default=0.0)
    average_pause: Mapped[float] = mapped_column(Float, default=0.0)
    fluency_score: Mapped[float] = mapped_column(Float, default=0.0)
    total_words: Mapped[int] = mapped_column(Integer, default=0)
    speech_duration: Mapped[float] = mapped_column(Float, default=0.0)
    # Extensible bag for future ML model outputs
    extra_metrics: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSONB, nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    session: Mapped[Optional["PracticeSession"]] = relationship(
        "PracticeSession", back_populates="fluency_metrics"
    )


class Conversation(Base):
    """A single chat turn (user or assistant) within a session."""

    __tablename__ = "conversations"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=_uuid
    )
    session_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("sessions.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    role: Mapped[str] = mapped_column(
        String(32), default=ConversationRole.USER.value
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    model_used: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    token_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    latency_ms: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    session: Mapped[Optional["PracticeSession"]] = relationship(
        "PracticeSession", back_populates="conversations"
    )
