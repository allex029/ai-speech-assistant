"""Timestamp and duration helpers."""

from datetime import datetime, timezone
from typing import Any, Optional


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def duration_seconds(
    start: datetime,
    end: Optional[datetime] = None,
) -> float:
    """Return elapsed seconds between two aware datetimes."""
    end = end or utc_now()
    if start.tzinfo is None:
        start = start.replace(tzinfo=timezone.utc)
    if end.tzinfo is None:
        end = end.replace(tzinfo=timezone.utc)
    return max(0.0, (end - start).total_seconds())


def normalize_word_timestamps(
    raw_segments: Optional[list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    """
    Normalize Groq/Whisper word or segment payloads into a common shape:

        [{"word": str, "start": float, "end": float}, ...]
    """
    if not raw_segments:
        return []

    normalized: list[dict[str, Any]] = []
    for item in raw_segments:
        word = item.get("word") or item.get("text") or ""
        start = item.get("start")
        end = item.get("end")
        if word and start is not None and end is not None:
            normalized.append(
                {
                    "word": str(word).strip(),
                    "start": float(start),
                    "end": float(end),
                }
            )
    return normalized


def speech_duration_from_timestamps(
    timestamps: list[dict[str, Any]],
) -> float:
    """Estimate total speech duration from first start to last end."""
    if not timestamps:
        return 0.0
    starts = [t["start"] for t in timestamps if "start" in t]
    ends = [t["end"] for t in timestamps if "end" in t]
    if not starts or not ends:
        return 0.0
    return max(0.0, max(ends) - min(starts))
