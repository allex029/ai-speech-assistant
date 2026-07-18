"""Session persistence service — no HTTP logic."""

from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.constants import ConversationRole, SessionStatus
from app.database.models import (
    Conversation,
    FluencyMetrics,
    PracticeSession,
    Transcript,
)
from app.utils.logger import get_logger
from app.utils.timestamps import duration_seconds, utc_now

logger = get_logger(__name__)


class SessionNotFoundError(Exception):
    def __init__(self, session_id: str):
        self.session_id = session_id
        super().__init__(f"Session '{session_id}' not found.")


class SessionService:
    """Responsible for saving and retrieving practice sessions."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def start_session(
        self,
        *,
        user_id: Optional[str] = None,
        title: Optional[str] = None,
        meta: Optional[dict[str, Any]] = None,
    ) -> PracticeSession:
        session = PracticeSession(
            user_id=user_id,
            title=title or "Practice Session",
            status=SessionStatus.ACTIVE.value,
            meta=meta,
            started_at=utc_now(),
        )
        self.db.add(session)
        await self.db.flush()
        await self.db.refresh(session)
        logger.info("Started session %s", session.id)
        return session

    async def end_session(self, session_id: str) -> PracticeSession:
        session = await self.get_session(session_id, with_relations=False)
        if session.status == SessionStatus.COMPLETED.value:
            return session

        session.ended_at = utc_now()
        session.status = SessionStatus.COMPLETED.value
        session.duration_seconds = duration_seconds(
            session.started_at,
            session.ended_at,
        )
        await self.db.flush()
        await self.db.refresh(session)
        logger.info(
            "Ended session %s (%.1fs)",
            session.id,
            session.duration_seconds or 0,
        )
        return session

    async def get_session(
        self,
        session_id: str,
        *,
        with_relations: bool = True,
    ) -> PracticeSession:
        stmt = select(PracticeSession).where(PracticeSession.id == session_id)
        if with_relations:
            stmt = stmt.options(
                selectinload(PracticeSession.transcripts),
                selectinload(PracticeSession.fluency_metrics),
                selectinload(PracticeSession.conversations),
            )
        result = await self.db.execute(stmt)
        session = result.scalar_one_or_none()
        if session is None:
            raise SessionNotFoundError(session_id)
        return session

    async def save_transcript(
        self,
        *,
        text: str,
        session_id: Optional[str] = None,
        duration: Optional[float] = None,
        timestamps: Optional[list[dict[str, Any]]] = None,
        language: Optional[str] = None,
        model_used: Optional[str] = None,
        audio_filename: Optional[str] = None,
    ) -> Transcript:
        record = Transcript(
            session_id=session_id,
            text=text,
            duration=duration,
            timestamps=timestamps,
            language=language,
            model_used=model_used,
            audio_filename=audio_filename,
        )
        self.db.add(record)
        await self.db.flush()
        await self.db.refresh(record)
        return record

    async def save_fluency_metrics(
        self,
        *,
        metrics: dict[str, Any],
        session_id: Optional[str] = None,
        transcript_id: Optional[str] = None,
    ) -> FluencyMetrics:
        record = FluencyMetrics(
            session_id=session_id,
            transcript_id=transcript_id,
            words_per_minute=metrics.get("words_per_minute", 0.0),
            filler_words=metrics.get("filler_words", []),
            filler_word_count=metrics.get("filler_word_count", 0),
            pause_count=metrics.get("pause_count", 0),
            longest_pause=metrics.get("longest_pause", 0.0),
            average_pause=metrics.get("average_pause", 0.0),
            fluency_score=metrics.get("fluency_score", 0.0),
            total_words=metrics.get("total_words", 0),
            speech_duration=metrics.get("speech_duration", 0.0),
            extra_metrics=metrics.get("extra_metrics"),
        )
        self.db.add(record)
        await self.db.flush()
        await self.db.refresh(record)
        return record

    async def save_conversation_turn(
        self,
        *,
        role: str,
        content: str,
        session_id: Optional[str] = None,
        model_used: Optional[str] = None,
        latency_ms: Optional[float] = None,
    ) -> Conversation:
        record = Conversation(
            session_id=session_id,
            role=role,
            content=content,
            model_used=model_used,
            latency_ms=latency_ms,
        )
        self.db.add(record)
        await self.db.flush()
        await self.db.refresh(record)
        return record

    async def get_conversation_history(
        self,
        session_id: str,
        limit: int = 20,
    ) -> list[dict[str, str]]:
        """Return recent turns as OpenAI-style message dicts."""
        stmt = (
            select(Conversation)
            .where(Conversation.session_id == session_id)
            .order_by(Conversation.created_at.asc())
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        rows = result.scalars().all()
        return [
            {
                "role": (
                    row.role
                    if row.role
                    in {
                        ConversationRole.USER.value,
                        ConversationRole.ASSISTANT.value,
                        ConversationRole.SYSTEM.value,
                    }
                    else ConversationRole.USER.value
                ),
                "content": row.content,
            }
            for row in rows
        ]
