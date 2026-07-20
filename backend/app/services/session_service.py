"""Session persistence service — no HTTP logic."""

from datetime import datetime, timezone
from typing import Any, Optional
from uuid import uuid4

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.constants import ConversationRole, SessionStatus
from app.database.models import (
    COLLECTION_CONVERSATIONS,
    COLLECTION_FLUENCY_METRICS,
    COLLECTION_SESSIONS,
    COLLECTION_TRANSCRIPTS,
)
from app.utils.logger import get_logger
from app.utils.timestamps import duration_seconds, utc_now

logger = get_logger(__name__)


def _uuid() -> str:
    return str(uuid4())


def _serialize(doc: Optional[dict]) -> Optional[dict]:
    """Convert MongoDB _id to id for Pydantic compatibility."""
    if doc is None:
        return None
    doc["id"] = str(doc.pop("_id"))
    return doc


def _serialize_many(docs: list[dict]) -> list[dict]:
    return [_serialize(d) for d in docs]


class SessionNotFoundError(Exception):
    def __init__(self, session_id: str):
        self.session_id = session_id
        super().__init__(f"Session '{session_id}' not found.")


class SessionService:
    """Responsible for saving and retrieving practice sessions."""

    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self.db = db

    async def start_session(
        self,
        *,
        user_id: Optional[str] = None,
        title: Optional[str] = None,
        meta: Optional[dict[str, Any]] = None,
    ) -> dict:
        now = utc_now()
        doc = {
            "_id": _uuid(),
            "user_id": user_id,
            "title": title or "Practice Session",
            "status": SessionStatus.ACTIVE.value,
            "meta": meta,
            "started_at": now,
            "ended_at": None,
            "duration_seconds": None,
            "created_at": now,
            "updated_at": now,
        }
        await self.db[COLLECTION_SESSIONS].insert_one(doc)
        logger.info("Started session %s", doc["_id"])
        return _serialize(doc)

    async def end_session(self, session_id: str) -> dict:
        session = await self.get_session(session_id, with_relations=False)
        if session["status"] == SessionStatus.COMPLETED.value:
            return session

        now = utc_now()
        ended_at = session["ended_at"] or now
        duration = duration_seconds(
            datetime.fromisoformat(session["started_at"]) if isinstance(session["started_at"], str) else session["started_at"],
            ended_at,
        )
        await self.db[COLLECTION_SESSIONS].update_one(
            {"_id": session_id},
            {
                "$set": {
                    "ended_at": ended_at,
                    "status": SessionStatus.COMPLETED.value,
                    "duration_seconds": duration,
                    "updated_at": now,
                }
            },
        )
        session["ended_at"] = ended_at
        session["status"] = SessionStatus.COMPLETED.value
        session["duration_seconds"] = duration
        logger.info("Ended session %s (%.1fs)", session_id, duration or 0)
        return session

    async def get_session(
        self,
        session_id: str,
        *,
        with_relations: bool = True,
    ) -> dict:
        doc = await self.db[COLLECTION_SESSIONS].find_one({"_id": session_id})
        if doc is None:
            raise SessionNotFoundError(session_id)

        session = _serialize(doc)

        if with_relations:
            transcripts = await self.db[COLLECTION_TRANSCRIPTS].find(
                {"session_id": session_id}
            ).to_list(length=None)
            fluency_metrics = await self.db[COLLECTION_FLUENCY_METRICS].find(
                {"session_id": session_id}
            ).to_list(length=None)
            conversations = await self.db[COLLECTION_CONVERSATIONS].find(
                {"session_id": session_id}
            ).to_list(length=None)

            session["transcripts"] = _serialize_many(transcripts)
            session["fluency_metrics"] = _serialize_many(fluency_metrics)
            session["conversations"] = _serialize_many(conversations)
        else:
            session["transcripts"] = []
            session["fluency_metrics"] = []
            session["conversations"] = []

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
    ) -> dict:
        doc = {
            "_id": _uuid(),
            "session_id": session_id,
            "text": text,
            "duration": duration,
            "timestamps": timestamps,
            "language": language,
            "model_used": model_used,
            "audio_filename": audio_filename,
            "pronunciation_data": None,
            "created_at": utc_now(),
        }
        await self.db[COLLECTION_TRANSCRIPTS].insert_one(doc)
        return _serialize(doc)

    async def save_fluency_metrics(
        self,
        *,
        metrics: dict[str, Any],
        session_id: Optional[str] = None,
        transcript_id: Optional[str] = None,
    ) -> dict:
        doc = {
            "_id": _uuid(),
            "session_id": session_id,
            "transcript_id": transcript_id,
            "words_per_minute": metrics.get("words_per_minute", 0.0),
            "filler_words": metrics.get("filler_words", []),
            "filler_word_count": metrics.get("filler_word_count", 0),
            "pause_count": metrics.get("pause_count", 0),
            "longest_pause": metrics.get("longest_pause", 0.0),
            "average_pause": metrics.get("average_pause", 0.0),
            "fluency_score": metrics.get("fluency_score", 0.0),
            "total_words": metrics.get("total_words", 0),
            "speech_duration": metrics.get("speech_duration", 0.0),
            "extra_metrics": metrics.get("extra_metrics"),
            "created_at": utc_now(),
        }
        await self.db[COLLECTION_FLUENCY_METRICS].insert_one(doc)
        return _serialize(doc)

    async def save_conversation_turn(
        self,
        *,
        role: str,
        content: str,
        session_id: Optional[str] = None,
        model_used: Optional[str] = None,
        latency_ms: Optional[float] = None,
    ) -> dict:
        doc = {
            "_id": _uuid(),
            "session_id": session_id,
            "role": role,
            "content": content,
            "model_used": model_used,
            "token_count": None,
            "latency_ms": latency_ms,
            "created_at": utc_now(),
        }
        await self.db[COLLECTION_CONVERSATIONS].insert_one(doc)
        return _serialize(doc)

    async def get_conversation_history(
        self,
        session_id: str,
        limit: int = 20,
    ) -> list[dict[str, str]]:
        """Return recent turns as OpenAI-style message dicts."""
        cursor = (
            self.db[COLLECTION_CONVERSATIONS]
            .find({"session_id": session_id})
            .sort("created_at", 1)
            .limit(limit)
        )
        rows = await cursor.to_list(length=limit)
        return [
            {
                "role": (
                    row["role"]
                    if row["role"]
                    in {
                        ConversationRole.USER.value,
                        ConversationRole.ASSISTANT.value,
                        ConversationRole.SYSTEM.value,
                    }
                    else ConversationRole.USER.value
                ),
                "content": row["content"],
            }
            for row in rows
        ]
