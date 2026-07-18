"""Application-wide constants."""

from enum import Enum


class SessionStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class ConversationRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


# Common English filler words used by FluencyService placeholders
FILLER_WORDS: frozenset[str] = frozenset(
    {
        "um",
        "uh",
        "uhm",
        "er",
        "ah",
        "like",
        "you know",
        "basically",
        "actually",
        "literally",
        "so",
        "well",
        "right",
        "okay",
        "ok",
        "hmm",
        "i mean",
        "kind of",
        "sort of",
    }
)

# Pause detection thresholds (seconds) — tunable without touching route logic
MIN_PAUSE_SECONDS: float = 0.3
LONG_PAUSE_SECONDS: float = 1.5

# Fluency scoring weights (placeholder algorithm)
FLUENCY_WEIGHT_WPM: float = 0.35
FLUENCY_WEIGHT_FILLERS: float = 0.25
FLUENCY_WEIGHT_PAUSES: float = 0.25
FLUENCY_WEIGHT_DURATION: float = 0.15

# Ideal speaking range for English learners (words per minute)
IDEAL_WPM_MIN: int = 110
IDEAL_WPM_MAX: int = 160

# Coach system prompt for Llama conversations
SPEAKING_COACH_SYSTEM_PROMPT: str = (
    "You are SpeakFlow, a friendly and encouraging AI English speaking coach. "
    "Respond conversationally to help the learner practice spoken English. "
    "Keep replies concise (2–4 sentences), correct gently when needed, "
    "ask follow-up questions, and never shame the learner for mistakes."
)

# Allowed audio file extensions
ALLOWED_AUDIO_EXTENSIONS: frozenset[str] = frozenset(
    {".wav", ".mp3", ".mpeg", ".webm", ".ogg", ".flac", ".m4a", ".mp4"}
)
