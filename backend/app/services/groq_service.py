"""Shared async HTTP client for the Groq OpenAI-compatible API."""

from typing import Any, Optional

import httpx

from app.core.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class GroqAPIError(Exception):
    """Raised when Groq returns a non-success response."""

    def __init__(self, message: str, status_code: int = 502, details: Any = None):
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(message)


class GroqService:
    """
    Low-level Groq API client.

    Higher-level services (Whisper, Llama) compose this class and
    never talk to httpx directly.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: float = 120.0,
    ) -> None:
        self.api_key = api_key if api_key is not None else settings.groq_api_key
        self.base_url = (base_url or settings.groq_base_url).rstrip("/")
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None

    def _ensure_api_key(self) -> None:
        if not self.api_key:
            raise GroqAPIError(
                "GROQ_API_KEY is not configured.",
                status_code=503,
            )

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=httpx.Timeout(self.timeout),
            )
        return self._client

    async def close(self) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    async def post_json(
        self,
        path: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        self._ensure_api_key()
        client = await self._get_client()
        try:
            response = await client.post(path, json=payload)
        except httpx.TimeoutException as exc:
            logger.error("Groq request timed out: %s", path)
            raise GroqAPIError("Groq API request timed out.", status_code=504) from exc
        except httpx.HTTPError as exc:
            logger.error("Groq HTTP error: %s", exc)
            raise GroqAPIError(
                f"Failed to reach Groq API: {exc}",
                status_code=502,
            ) from exc

        return self._handle_response(response)

    async def post_multipart(
        self,
        path: str,
        files: dict[str, Any],
        data: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        self._ensure_api_key()
        client = await self._get_client()
        try:
            response = await client.post(path, files=files, data=data or {})
        except httpx.TimeoutException as exc:
            logger.error("Groq multipart request timed out: %s", path)
            raise GroqAPIError("Groq API request timed out.", status_code=504) from exc
        except httpx.HTTPError as exc:
            logger.error("Groq HTTP error: %s", exc)
            raise GroqAPIError(
                f"Failed to reach Groq API: {exc}",
                status_code=502,
            ) from exc

        return self._handle_response(response)

    def _handle_response(self, response: httpx.Response) -> dict[str, Any]:
        if response.status_code >= 400:
            try:
                body = response.json()
            except Exception:
                body = response.text
            logger.error(
                "Groq error %s: %s",
                response.status_code,
                body,
            )
            raise GroqAPIError(
                f"Groq API error ({response.status_code}).",
                status_code=502,
                details=body,
            )
        return response.json()


# Module-level singleton for dependency injection
_groq_service: Optional[GroqService] = None


def get_groq_service() -> GroqService:
    global _groq_service
    if _groq_service is None:
        _groq_service = GroqService()
    return _groq_service
