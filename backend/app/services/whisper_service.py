"""Whisper transcription via Groq."""

from typing import Any, Optional

from app.core.config import settings
from app.schemas.speech import TranscribeResponse, WordTimestamp
from app.services.groq_service import GroqService, get_groq_service
from app.utils.logger import get_logger
from app.utils.timestamps import normalize_word_timestamps, speech_duration_from_timestamps

logger = get_logger(__name__)


class WhisperService:
    """
    Responsible only for:
      - sending audio to Groq Whisper
      - receiving transcript
      - returning timestamps
    """

    def __init__(self, groq: Optional[GroqService] = None) -> None:
        self.groq = groq or get_groq_service()
        self.model = settings.whisper_model

    async def transcribe(
        self,
        audio_bytes: bytes,
        filename: str = "audio.webm",
        language: Optional[str] = "en",
    ) -> TranscribeResponse:
        """Transcribe audio and return transcript + word timestamps."""
        logger.info(
            "Transcribing %s bytes with model=%s",
            len(audio_bytes),
            self.model,
        )

        files = {
            "file": (filename, audio_bytes, "application/octet-stream"),
        }
        data: dict[str, Any] = {
            "model": self.model,
            "response_format": "verbose_json",
            "timestamp_granularities[]": "word",
        }
        if language:
            data["language"] = language

        result = await self.groq.post_multipart(
            "/audio/transcriptions",
            files=files,
            data=data,
        )

        transcript = (result.get("text") or "").strip()
        raw_words = result.get("words") or []

        # Fallback: flatten segments if word-level timestamps absent
        if not raw_words and result.get("segments"):
            raw_words = []
            for segment in result["segments"]:
                if "words" in segment:
                    raw_words.extend(segment["words"])
                else:
                    raw_words.append(
                        {
                            "word": segment.get("text", "").strip(),
                            "start": segment.get("start", 0.0),
                            "end": segment.get("end", 0.0),
                        }
                    )

        timestamps_raw = normalize_word_timestamps(raw_words)
        timestamps = [WordTimestamp(**t) for t in timestamps_raw]

        duration = float(result.get("duration") or 0.0)
        if duration <= 0 and timestamps_raw:
            duration = speech_duration_from_timestamps(timestamps_raw)

        return TranscribeResponse(
            transcript=transcript,
            timestamps=timestamps,
            duration=round(duration, 3),
            pronunciation_data=None,  # future hook
            language=result.get("language") or language,
            model_used=self.model,
        )


def get_whisper_service() -> WhisperService:
    return WhisperService()
