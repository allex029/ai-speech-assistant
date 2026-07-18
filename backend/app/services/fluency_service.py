"""Fluency analysis — placeholder calculations, ML-swappable design."""

from abc import ABC, abstractmethod
from typing import Any, Optional

from app.core.constants import (
    FILLER_WORDS,
    FLUENCY_WEIGHT_DURATION,
    FLUENCY_WEIGHT_FILLERS,
    FLUENCY_WEIGHT_PAUSES,
    FLUENCY_WEIGHT_WPM,
    IDEAL_WPM_MAX,
    IDEAL_WPM_MIN,
    MIN_PAUSE_SECONDS,
)
from app.schemas.session import FluencyAnalyzeResponse
from app.utils.helpers import clamp, count_words, tokenize_words, unique_preserve_order
from app.utils.logger import get_logger
from app.utils.timestamps import normalize_word_timestamps, speech_duration_from_timestamps

logger = get_logger(__name__)


class FluencyAnalyzer(ABC):
    """
    Strategy interface for fluency scoring.

    Swap PlaceholderFluencyAnalyzer for an ML-backed implementation
    without changing FluencyService or API routes.
    """

    @abstractmethod
    def analyze(
        self,
        transcript: str,
        timestamps: list[dict[str, Any]],
    ) -> FluencyAnalyzeResponse:
        raise NotImplementedError


class PlaceholderFluencyAnalyzer(FluencyAnalyzer):
    """
    Heuristic fluency metrics suitable for early product iterations.

    Responsibilities covered:
      - pause detection
      - filler word detection
      - WPM
      - speech duration
    """

    def analyze(
        self,
        transcript: str,
        timestamps: list[dict[str, Any]],
    ) -> FluencyAnalyzeResponse:
        words = tokenize_words(transcript)
        total_words = len(words) if words else count_words(transcript)

        normalized = normalize_word_timestamps(timestamps)
        speech_duration = speech_duration_from_timestamps(normalized)

        # If timestamps missing, estimate ~2.5 words/sec as a soft fallback
        if speech_duration <= 0 and total_words > 0:
            speech_duration = total_words / 2.5

        minutes = speech_duration / 60.0 if speech_duration > 0 else 0.0
        wpm = (total_words / minutes) if minutes > 0 else 0.0

        filler_hits = self._detect_fillers(words)
        pauses = self._detect_pauses(normalized)
        pause_count = len(pauses)
        longest_pause = max(pauses) if pauses else 0.0
        average_pause = (sum(pauses) / pause_count) if pause_count else 0.0

        score = self._compute_score(
            wpm=wpm,
            filler_count=len(filler_hits),
            total_words=total_words,
            pause_count=pause_count,
            speech_duration=speech_duration,
        )

        return FluencyAnalyzeResponse(
            words_per_minute=round(wpm, 2),
            filler_words=unique_preserve_order(filler_hits),
            pause_count=pause_count,
            longest_pause=round(longest_pause, 3),
            average_pause=round(average_pause, 3),
            fluency_score=round(score, 2),
            total_words=total_words,
            speech_duration=round(speech_duration, 3),
            filler_word_count=len(filler_hits),
        )

    def _detect_fillers(self, words: list[str]) -> list[str]:
        hits: list[str] = []
        # Multi-word fillers first
        joined = " ".join(words)
        for phrase in ("you know", "i mean", "kind of", "sort of"):
            if phrase in joined:
                hits.extend([phrase] * joined.count(phrase))

        single_fillers = FILLER_WORDS - {"you know", "i mean", "kind of", "sort of"}
        for word in words:
            if word in single_fillers:
                hits.append(word)
        return hits

    def _detect_pauses(self, timestamps: list[dict[str, Any]]) -> list[float]:
        pauses: list[float] = []
        for i in range(1, len(timestamps)):
            gap = timestamps[i]["start"] - timestamps[i - 1]["end"]
            if gap >= MIN_PAUSE_SECONDS:
                pauses.append(gap)
        return pauses

    def _compute_score(
        self,
        *,
        wpm: float,
        filler_count: int,
        total_words: int,
        pause_count: int,
        speech_duration: float,
    ) -> float:
        # WPM component — peak inside ideal range
        if IDEAL_WPM_MIN <= wpm <= IDEAL_WPM_MAX:
            wpm_score = 100.0
        elif wpm < IDEAL_WPM_MIN:
            wpm_score = clamp((wpm / IDEAL_WPM_MIN) * 100)
        else:
            overshoot = wpm - IDEAL_WPM_MAX
            wpm_score = clamp(100 - overshoot * 0.5)

        # Filler density (per 100 words)
        filler_rate = (filler_count / total_words * 100) if total_words else 0.0
        filler_score = clamp(100 - filler_rate * 8)

        # Pause density (pauses per minute)
        minutes = speech_duration / 60.0 if speech_duration > 0 else 1.0
        pauses_per_min = pause_count / minutes
        pause_score = clamp(100 - pauses_per_min * 10)

        # Duration — prefer at least ~5 seconds of speech
        duration_score = clamp((speech_duration / 5.0) * 100) if speech_duration else 0.0

        return (
            wpm_score * FLUENCY_WEIGHT_WPM
            + filler_score * FLUENCY_WEIGHT_FILLERS
            + pause_score * FLUENCY_WEIGHT_PAUSES
            + duration_score * FLUENCY_WEIGHT_DURATION
        )


class FluencyService:
    """
    Facade over a FluencyAnalyzer strategy.

    No API / HTTP logic lives here — routes call this service only.
    """

    def __init__(self, analyzer: Optional[FluencyAnalyzer] = None) -> None:
        self.analyzer = analyzer or PlaceholderFluencyAnalyzer()

    def analyze(
        self,
        transcript: str,
        timestamps: Optional[list[dict[str, Any]]] = None,
    ) -> FluencyAnalyzeResponse:
        logger.info("Analyzing fluency for transcript length=%s", len(transcript))
        return self.analyzer.analyze(transcript, timestamps or [])

    def set_analyzer(self, analyzer: FluencyAnalyzer) -> None:
        """Hot-swap analyzer (e.g. load an ML model later)."""
        self.analyzer = analyzer


def get_fluency_service() -> FluencyService:
    return FluencyService()
