"""Chat validation tests (mocked Llama)."""

from unittest.mock import AsyncMock

from fastapi.testclient import TestClient

from app.main import app
from app.schemas.chat import ChatResponse
from app.services.llama_service import get_llama_service


class _FakeLlama:
    async def generate_response(self, transcript, **kwargs):
        return ChatResponse(
            response=f"Echo: {transcript}",
            model_used="fake-llama",
            latency_ms=1.0,
        )


def test_chat_endpoint_with_mock():
    app.dependency_overrides[get_llama_service] = lambda: _FakeLlama()
    client = TestClient(app)

    async def _no_db():
        yield AsyncMock()

    from app.database.database import get_database

    app.dependency_overrides[get_database] = _no_db

    try:
        response = client.post("/api/chat", json={"transcript": "Hello coach"})
        assert response.status_code == 200
        body = response.json()
        assert body["response"] == "Echo: Hello coach"
        assert body["model_used"] == "fake-llama"
    finally:
        app.dependency_overrides.clear()


def test_chat_rejects_empty_transcript():
    async def _no_db():
        yield AsyncMock()

    from app.database.database import get_database

    app.dependency_overrides[get_database] = _no_db
    client = TestClient(app)
    try:
        response = client.post("/api/chat", json={"transcript": ""})
        assert response.status_code == 422
    finally:
        app.dependency_overrides.clear()
