"""Llama conversation generation via Groq."""

import time
from typing import Any, Optional

from app.core.config import settings
from app.core.constants import SPEAKING_COACH_SYSTEM_PROMPT
from app.schemas.chat import ChatResponse
from app.services.groq_service import GroqService, get_groq_service
from app.utils.logger import get_logger

logger = get_logger(__name__)


class LlamaService:
    """Responsible only for conversation generation."""

    def __init__(self, groq: Optional[GroqService] = None) -> None:
        self.groq = groq or get_groq_service()
        self.model = settings.llama_model or settings.model_name

    async def generate_response(
        self,
        transcript: str,
        *,
        system_prompt: Optional[str] = None,
        history: Optional[list[dict[str, str]]] = None,
        temperature: float = 0.7,
        max_tokens: int = 512,
    ) -> ChatResponse:
        """
        Generate a coaching reply for the learner's transcript.

        `history` is an optional list of {"role", "content"} messages
        for multi-turn session context.
        """
        messages: list[dict[str, Any]] = [
            {
                "role": "system",
                "content": system_prompt or SPEAKING_COACH_SYSTEM_PROMPT,
            }
        ]
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": transcript})

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        logger.info("Generating chat response with model=%s", self.model)
        started = time.perf_counter()
        result = await self.groq.post_json("/chat/completions", payload)
        latency_ms = (time.perf_counter() - started) * 1000

        choices = result.get("choices") or []
        if not choices:
            logger.warning("Groq chat completion returned no choices")
            content = (
                "I'm having trouble responding right now. "
                "Could you try saying that again?"
            )
        else:
            content = (
                choices[0].get("message", {}).get("content") or ""
            ).strip()

        return ChatResponse(
            response=content,
            model_used=self.model,
            latency_ms=round(latency_ms, 2),
        )


def get_llama_service() -> LlamaService:
    return LlamaService()
