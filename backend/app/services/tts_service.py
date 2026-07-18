"""
Text-to-speech service — Piper integration stub.

Designed so the Practice page can later call TTS without rewriting routes.
"""

from abc import ABC, abstractmethod
from typing import Optional

from app.utils.logger import get_logger

logger = get_logger(__name__)


class TTSProvider(ABC):
    @abstractmethod
    async def synthesize(self, text: str, voice: Optional[str] = None) -> bytes:
        raise NotImplementedError


class PiperTTSProvider(TTSProvider):
    """
    Future Piper integration.

    When Piper is installed locally or via a sidecar container,
    implement process invocation or HTTP call here.
    """

    async def synthesize(self, text: str, voice: Optional[str] = None) -> bytes:
        logger.warning(
            "Piper TTS not yet configured — returning empty audio for text length=%s",
            len(text),
        )
        # Placeholder: empty WAV header would go here; callers should handle empty bytes.
        return b""


class TTSService:
    """Facade for text-to-speech. Swap providers without touching API routes."""

    def __init__(self, provider: Optional[TTSProvider] = None) -> None:
        self.provider = provider or PiperTTSProvider()

    async def synthesize(self, text: str, voice: Optional[str] = None) -> bytes:
        if not text.strip():
            return b""
        return await self.provider.synthesize(text, voice=voice)

    def set_provider(self, provider: TTSProvider) -> None:
        self.provider = provider


def get_tts_service() -> TTSService:
    return TTSService()
