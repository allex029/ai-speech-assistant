"""Fluency service unit tests (no external APIs)."""

from app.services.fluency_service import FluencyService, PlaceholderFluencyAnalyzer


def test_fluency_detects_fillers_and_wpm():
    service = FluencyService(analyzer=PlaceholderFluencyAnalyzer())
    timestamps = [
        {"word": "um", "start": 0.0, "end": 0.2},
        {"word": "I", "start": 0.5, "end": 0.6},
        {"word": "like", "start": 0.7, "end": 0.9},
        {"word": "learning", "start": 1.0, "end": 1.4},
        {"word": "English", "start": 1.5, "end": 2.0},
    ]
    result = service.analyze("um I like learning English", timestamps)

    assert result.total_words == 5
    assert "um" in result.filler_words
    assert result.pause_count >= 1
    assert result.words_per_minute > 0
    assert 0 <= result.fluency_score <= 100


def test_fluency_handles_empty_timestamps():
    service = FluencyService()
    result = service.analyze("Hello world this is a test", [])
    assert result.total_words == 6
    assert result.pause_count == 0
    assert result.words_per_minute > 0
