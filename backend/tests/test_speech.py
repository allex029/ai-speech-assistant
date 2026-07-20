"""Speech upload validation tests."""

from io import BytesIO
from unittest.mock import AsyncMock

from fastapi.testclient import TestClient

from app.main import app
from app.database.database import get_database
from app.schemas.speech import TranscribeResponse, WordTimestamp
from app.services.whisper_service import get_whisper_service


class _FakeWhisper:
    async def transcribe(self, audio_bytes, filename="audio.webm", language="en"):
        return TranscribeResponse(
            transcript="hello world",
            timestamps=[
                WordTimestamp(word="hello", start=0.0, end=0.4),
                WordTimestamp(word="world", start=0.5, end=0.9),
            ],
            duration=1.0,
            model_used="fake-whisper",
        )


def test_transcribe_rejects_missing_file():
    async def _no_db():
        yield AsyncMock()

    app.dependency_overrides[get_database] = _no_db
    client = TestClient(app)
    try:
        response = client.post("/api/speech/transcribe")
        assert response.status_code == 422
    finally:
        app.dependency_overrides.clear()


def test_transcribe_rejects_invalid_extension():
    async def _no_db():
        yield AsyncMock()

    app.dependency_overrides[get_database] = _no_db
    app.dependency_overrides[get_whisper_service] = lambda: _FakeWhisper()
    client = TestClient(app)

    try:
        response = client.post(
            "/api/speech/transcribe",
            files={"file": ("notes.txt", BytesIO(b"not audio"), "text/plain")},
        )
        assert response.status_code == 400
        assert response.json()["error_code"] == "audio_validation_error"
    finally:
        app.dependency_overrides.clear()


def test_transcribe_success_with_mock():
    async def _no_db():
        yield AsyncMock()

    app.dependency_overrides[get_database] = _no_db
    app.dependency_overrides[get_whisper_service] = lambda: _FakeWhisper()
    client = TestClient(app)

    try:
        response = client.post(
            "/api/speech/transcribe",
            files={"file": ("sample.webm", BytesIO(b"fake-audio-bytes"), "audio/webm")},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["transcript"] == "hello world"
        assert body["duration"] == 1.0
        assert len(body["timestamps"]) == 2
    finally:
        app.dependency_overrides.clear()
