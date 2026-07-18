"""Audio validation and lightweight metadata helpers."""

import io
from pathlib import Path
from typing import Optional

from fastapi import UploadFile

from app.core.config import settings
from app.core.constants import ALLOWED_AUDIO_EXTENSIONS


class AudioValidationError(Exception):
    """Raised when uploaded audio fails validation."""

    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


async def read_and_validate_audio(file: UploadFile) -> bytes:
    """
    Read an uploaded audio file and validate size / type.

    Returns raw bytes suitable for forwarding to Whisper.
    """
    if file is None or not file.filename:
        raise AudioValidationError("Missing audio file.", status_code=400)

    extension = Path(file.filename).suffix.lower()
    if extension not in ALLOWED_AUDIO_EXTENSIONS:
        raise AudioValidationError(
            f"Invalid audio file type '{extension}'. "
            f"Allowed: {', '.join(sorted(ALLOWED_AUDIO_EXTENSIONS))}",
            status_code=400,
        )

    content_type = (file.content_type or "").lower()
    allowed_types = settings.allowed_audio_types_list
    # Some browsers send empty or generic content types — rely on extension then
    if content_type and content_type not in allowed_types and content_type != "application/octet-stream":
        # Soft check: allow if extension is valid
        pass

    data = await file.read()
    if not data:
        raise AudioValidationError("Audio file is empty.", status_code=400)

    if len(data) > settings.max_audio_size_bytes:
        raise AudioValidationError(
            f"Audio file exceeds maximum size of {settings.max_audio_size_mb} MB.",
            status_code=413,
        )

    return data


def estimate_duration_seconds(audio_bytes: bytes, sample_rate: int = 16000) -> Optional[float]:
    """
    Best-effort duration estimate.

    Prefer Whisper-reported duration when available. This helper avoids
    hard dependency on librosa at import time for lightweight validation paths.
    """
    try:
        import librosa  # noqa: WPS433 — optional heavy import

        y, sr = librosa.load(io.BytesIO(audio_bytes), sr=None)
        return float(librosa.get_duration(y=y, sr=sr))
    except Exception:
        # Fallback: rough estimate for 16-bit mono PCM-like payloads
        if len(audio_bytes) > 44:
            return len(audio_bytes) / (sample_rate * 2)
        return None
