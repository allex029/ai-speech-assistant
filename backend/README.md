# SpeakFlow Backend

Production-oriented FastAPI backend for **SpeakFlow**, an AI English Speaking Coach. It provides speech transcription (Groq Whisper), conversational coaching (Llama 3 via Groq), fluency analysis, and practice session persistence — with a modular layout ready for auth, streaming, Redis, Celery, and TTS (Piper).

## Tech Stack

| Layer | Technology |
|-------|------------|
| Runtime | Python 3.12+ |
| API | FastAPI + Uvicorn |
| Validation | Pydantic v2 / pydantic-settings |
| ORM | SQLAlchemy 2.0 (async) |
| Migrations | Alembic |
| Database | PostgreSQL |
| HTTP client | httpx |
| STT | Groq Whisper Large V3 Turbo |
| LLM | Llama 3 (Groq) |
| Audio / analytics | Librosa, NumPy, Pandas |
| TTS (stub) | Piper (future) |

## Installation

```bash
cd backend

# Create and activate a virtual environment
python3.12 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and set GROQ_API_KEY + DATABASE_URL
```

### PostgreSQL

Create a database (example):

```bash
createdb speakflow
# or via psql:
# CREATE DATABASE speakflow;
```

Run migrations:

```bash
alembic upgrade head
```

## Running

```bash
# From the backend/ directory with the venv active
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- Interactive docs: http://localhost:8000/docs  
- ReDoc: http://localhost:8000/redoc  
- Health: http://localhost:8000/api/health  

Point the React frontend (`http://localhost:5173`) at this API via your Vite proxy or `VITE_API_URL`.

## Folder Structure

```
backend/
├── app/
│   ├── api/
│   │   ├── routes/          # Thin HTTP handlers (no business logic)
│   │   │   ├── auth.py      # JWT/OAuth scaffolding (501 for now)
│   │   │   ├── speech.py    # POST /speech/transcribe
│   │   │   ├── chat.py      # POST /chat
│   │   │   ├── fluency.py   # POST /fluency/analyze
│   │   │   ├── sessions.py  # Session start / end / get
│   │   │   └── health.py
│   │   └── router.py        # Aggregates all route modules
│   ├── core/
│   │   ├── config.py        # Pydantic Settings (env-driven)
│   │   ├── security.py      # Password hashing + JWT helpers
│   │   └── constants.py     # Enums, filler words, coach prompt
│   ├── database/
│   │   ├── database.py      # Async engine + session dependency
│   │   ├── models.py        # User, Session, Transcript, …
│   │   └── migrations/      # Alembic env + versions
│   ├── schemas/             # Request/response DTOs
│   ├── services/            # Groq, Whisper, Llama, Fluency, Session, TTS
│   ├── utils/               # Audio, timestamps, helpers, logger
│   ├── middleware/          # Request logging + exception handlers
│   └── main.py              # App factory + lifespan
├── tests/
├── .env.example
├── requirements.txt
├── alembic.ini
└── README.md
```

## Architecture

```
React Frontend
      │
      ▼
FastAPI Router          ← validation, auth hooks, HTTP only
      │
      ▼
Service Layer           ← Whisper / Llama / Fluency / Session / TTS
      │
      ├──► Groq APIs (Whisper + Llama)
      └──► PostgreSQL (SQLAlchemy)
```

Speech pipeline:

```
Audio
   │
   ▼
Whisper (Groq)
   │
   ▼
Transcript + Timestamps
   │
   ├──► Fluency Analysis
   │
   └──► Llama 3
            │
            ▼
      AI Response
```

Routes never call Groq or compute fluency themselves. Services are injectable and strategy-based (e.g. `FluencyAnalyzer`, `TTSProvider`) so ML models and Piper can replace placeholders without rewriting endpoints.

## API Endpoints

### Health

`GET /api/health`

```json
{ "status": "running" }
```

### Speech

`POST /api/speech/transcribe`  
`multipart/form-data`: `file` (required), optional `session_id`, `language`

```json
{
  "transcript": "I love learning English.",
  "timestamps": [{ "word": "I", "start": 0.0, "end": 0.2 }],
  "duration": 1.4,
  "pronunciation_data": null
}
```

### Chat

`POST /api/chat`

```json
{ "transcript": "I love learning English.", "session_id": null }
```

```json
{ "response": "That's wonderful! What do you enjoy most about it?" }
```

### Fluency

`POST /api/fluency/analyze`

```json
{
  "transcript": "um I like learning English",
  "timestamps": [
    { "word": "um", "start": 0.0, "end": 0.2 },
    { "word": "I", "start": 0.5, "end": 0.6 }
  ]
}
```

```json
{
  "words_per_minute": 120.0,
  "filler_words": ["um", "like"],
  "pause_count": 1,
  "longest_pause": 0.3,
  "average_pause": 0.3,
  "fluency_score": 82.5
}
```

### Session

| Method | Path | Purpose |
|--------|------|---------|
| `POST` | `/api/session/start` | Create a practice session |
| `POST` | `/api/session/end` | Body: `{ "session_id": "…" }` |
| `GET` | `/api/session/{id}` | Session + transcripts, metrics, conversations |

### Auth (scaffolding)

`POST /api/auth/register` and `POST /api/auth/login` return `501` until JWT auth is enabled. Password hashing and token helpers already live in `app/core/security.py`.

## Environment Variables

| Variable | Description |
|----------|-------------|
| `GROQ_API_KEY` | Groq API key (required for STT/LLM) |
| `DATABASE_URL` | Async SQLAlchemy URL (`postgresql+asyncpg://…`) |
| `MODEL_NAME` | Default chat model alias |
| `WHISPER_MODEL` | e.g. `whisper-large-v3-turbo` |
| `LLAMA_MODEL` | e.g. `llama-3.3-70b-versatile` |
| `CORS_ORIGINS` | Comma-separated frontend origins |
| `SECRET_KEY` | JWT signing secret (change in production) |
| `LOG_LEVEL` | `DEBUG`, `INFO`, `WARNING`, … |

See `.env.example` for the full list.

## Error Handling

Central handlers map domain errors to HTTP responses:

| Condition | Status | `error_code` |
|-----------|--------|--------------|
| Missing / invalid audio | 400 / 413 | `audio_validation_error` |
| Validation (Pydantic) | 422 | `validation_error` |
| Groq failures / timeouts | 502 / 504 / 503 | `groq_api_error` |
| Session not found | 404 | `session_not_found` |
| Database errors | 500 | `database_error` |

## Logging

`RequestLoggingMiddleware` logs every request method/path, status code, and duration (`X-Process-Time-Ms` response header). Errors are logged with stack traces via the shared `speakflow` logger.

## Testing

```bash
pytest -q
```

Tests cover health, fluency heuristics, chat (mocked Llama), and speech validation (mocked Whisper) without requiring a live Groq key.

## Future Extensions

The codebase is intentionally shaped for:

- **JWT / OAuth** — wire `security.py` into route dependencies  
- **Pronunciation scoring** — `pronunciation_data` on transcripts  
- **Redis + Celery** — offload long audio jobs  
- **WebSockets / streaming** — stream Llama tokens to the Practice UI  
- **Piper TTS** — implement `PiperTTSProvider.synthesize`  
- **Docker / Kubernetes** — add a Dockerfile using this same package layout  

## Project Documentation

Detailed architecture write-ups live in the monorepo:

- [`../docs/backend.md`](../docs/backend.md)  
- [`../docs/frontend.md`](../docs/frontend.md)  

## License

Part of the SpeakFlow / AI Speech Assistant project.
