# SpeakFlow Backend Documentation

This document explains the production-oriented FastAPI backend for **SpeakFlow**. A new engineer should be able to navigate architecture, request flow, AI integrations, and extension points without reading every module first.

Companion docs: [`frontend.md`](./frontend.md) · Backend README: [`../backend/README.md`](../backend/README.md)

---

## 1. Why This Architecture

The backend deliberately avoids a single-file FastAPI tutorial layout. Goals:

| Goal | How it is achieved |
|------|--------------------|
| Modularity | Routes / services / schemas / models are separate packages |
| Testability | Services are injectable; Groq and DB can be mocked |
| Scalability | Async I/O, connection pooling, Alembic migrations |
| Future features | Strategy interfaces for fluency & TTS; JWT helpers ready |
| Operability | Structured logging middleware + centralized exception handlers |

This matches a typical AI SaaS service layout: thin HTTP edge, rich domain services, persistent store.

---

## 2. High-Level Architecture

```
React Frontend
      │
      ▼
FastAPI Router
      │
      ▼
Service Layer
      │
      ├──► Groq APIs (Whisper + Llama)
      └──► PostgreSQL
```

### Layer responsibilities

```
┌─────────────────────────────────────────────────────────┐
│  api/routes     HTTP adapters, Depends(), status codes  │
├─────────────────────────────────────────────────────────┤
│  schemas        Pydantic request/response contracts     │
├─────────────────────────────────────────────────────────┤
│  services       Business + AI orchestration             │
├─────────────────────────────────────────────────────────┤
│  database       SQLAlchemy models + async sessions      │
├─────────────────────────────────────────────────────────┤
│  core           Settings, security, constants           │
├─────────────────────────────────────────────────────────┤
│  middleware     Logging, exception → JSON mapping       │
├─────────────────────────────────────────────────────────┤
│  utils          Audio validation, timestamps, logging   │
└─────────────────────────────────────────────────────────┘
```

**Rule:** no business logic inside API routes. Routes validate input, call a service, map the result to a schema.

---

## 3. Folder Structure & Responsibilities

```
backend/app/
├── api/
│   ├── router.py              Mounts all route modules under /api
│   └── routes/
│       ├── health.py          Liveness
│       ├── auth.py            Future JWT/OAuth (501 stubs)
│       ├── speech.py          Transcription endpoint
│       ├── chat.py            Coaching chat endpoint
│       ├── fluency.py         Fluency analysis endpoint
│       └── sessions.py        Session lifecycle
├── core/
│   ├── config.py              pydantic-settings (env only — no hardcoded keys)
│   ├── security.py            bcrypt + JWT encode/decode
│   └── constants.py           Filler words, pause thresholds, coach prompt
├── database/
│   ├── database.py            Engine, session factory, get_db
│   ├── models.py              ORM entities
│   └── migrations/            Alembic env + versions
├── schemas/                   API DTOs (speech, chat, session, user)
├── services/
│   ├── groq_service.py        Shared async httpx client for Groq
│   ├── whisper_service.py     STT only
│   ├── llama_service.py       Chat completions only
│   ├── fluency_service.py     Pause / filler / WPM / score
│   ├── session_service.py     Persist sessions & related rows
│   └── tts_service.py         Piper stub (swappable provider)
├── utils/
│   ├── audio.py               Upload validation
│   ├── timestamps.py          Word-timestamp normalization
│   ├── helpers.py             Tokenize / clamp / etc.
│   └── logger.py              Logging setup
├── middleware/
│   ├── logging.py             Request timing
│   └── exception_handler.py   Domain → HTTP mapping
└── main.py                    create_app() + lifespan
```

---

## 4. Request Lifecycle

```
1. Client HTTP request
2. CORSMiddleware
3. RequestLoggingMiddleware   → log "→ METHOD path"
4. Route matching + Pydantic validation
5. Depends() injection        → db session, services
6. Route handler              → service call
7. Service                    → Groq / DB / heuristics
8. Response model serialization
9. Logging middleware         → log "← status duration"
10. Exception handlers (if any error along the way)
```

Example — transcribe:

```
POST /api/speech/transcribe (multipart file)
        │
        ▼
read_and_validate_audio()
        │
        ▼
WhisperService.transcribe()
        │
        ▼
GroqService.post_multipart("/audio/transcriptions")
        │
        ▼
normalize timestamps → TranscribeResponse
        │
        ▼ (optional session_id)
SessionService.save_transcript()
```

---

## 5. Configuration

All runtime config flows through `app.core.config.Settings` (Pydantic Settings).

Critical variables:

| Env var | Role |
|---------|------|
| `GROQ_API_KEY` | Authenticates Groq calls |
| `DATABASE_URL` | `postgresql+asyncpg://…` for the app |
| `WHISPER_MODEL` | Default `whisper-large-v3-turbo` |
| `LLAMA_MODEL` / `MODEL_NAME` | Chat model ids |
| `CORS_ORIGINS` | Frontend origins |
| `SECRET_KEY` | Future JWT signing |

Never hardcode API keys, model names, or DB URLs in services. Read from `settings`.

Alembic uses `settings.sync_database_url` (asyncpg URL rewritten to `psycopg2`).

---

## 6. API Surface

| Method | Path | Service |
|--------|------|---------|
| GET | `/api/health` | — |
| POST | `/api/speech/transcribe` | WhisperService |
| POST | `/api/chat` | LlamaService |
| POST | `/api/fluency/analyze` | FluencyService |
| POST | `/api/session/start` | SessionService |
| POST | `/api/session/end` | SessionService |
| GET | `/api/session/{id}` | SessionService |
| POST | `/api/auth/*` | 501 scaffolding |

Interactive OpenAPI: `/docs`.

---

## 7. Service Layer

### GroqService

Shared async HTTP client (`httpx.AsyncClient`). Handles:

- Auth header
- Timeouts
- JSON and multipart posts
- Mapping transport/API failures → `GroqAPIError`

Whisper and Llama never open their own HTTP clients.

### WhisperService

**Only** responsible for:

1. Sending audio to Groq Whisper  
2. Receiving transcript text  
3. Returning word timestamps (+ duration)

Output shape matches the frontend Practice needs and leaves `pronunciation_data=None` as a future hook.

### LlamaService

**Only** responsible for conversation generation. Builds messages with the SpeakFlow coach system prompt, optional session history, and returns `ChatResponse`.

### FluencyService

Owns pause detection, filler detection, WPM, speech duration, and a composite fluency score.

```
FluencyService
      │
      ▼
FluencyAnalyzer (ABC)
      │
      ├── PlaceholderFluencyAnalyzer   ← current
      └── (future) MLFluencyAnalyzer
```

Routes call `FluencyService.analyze(...)` only. Swap analyzers with `set_analyzer()` or DI — no route changes.

### SessionService

Persists `PracticeSession`, `Transcript`, `FluencyMetrics`, and `Conversation` rows. Loads conversation history for multi-turn chat. Contains **no** FastAPI imports.

### TTSService

`TTSProvider` ABC with `PiperTTSProvider` stub returning empty bytes until Piper is integrated.

---

## 8. AI Integrations

### Whisper workflow

```
Audio bytes
   │
   ▼
Whisper (Groq)  model=WHISPER_MODEL
   │
   ▼
verbose_json + word timestamps
   │
   ▼
Transcript + Timestamps + Duration
```

### Llama workflow

```
User transcript (+ optional history)
   │
   ▼
Chat Completions (Groq)  model=LLAMA_MODEL
   │
   ▼
Assistant text response
```

### Combined coaching pipeline

```
Audio
   │
   ▼
Whisper
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
            │
            ▼ (future)
         Piper TTS
```

---

## 9. Fluency Analysis Pipeline

```
transcript + timestamps
        │
        ├─ tokenize words
        ├─ detect fillers (dictionary + multi-word phrases)
        ├─ detect pauses (gap ≥ MIN_PAUSE_SECONDS between words)
        ├─ compute duration (first start → last end)
        ├─ compute WPM
        └─ weighted score (WPM, fillers, pauses, duration)
                │
                ▼
        FluencyAnalyzeResponse
```

Weights and thresholds live in `core/constants.py` so product can tune them without editing analyzer code.

Placeholder math is intentionally simple. An ML model can emit the same `FluencyAnalyzeResponse` fields (and stash extras in `extra_metrics` on the DB model).

---

## 10. Database Layer

### Entities & relationships

```
User 1───* PracticeSession
                │
                ├──* Transcript
                ├──* FluencyMetrics  (optional FK → Transcript)
                └──* Conversation
```

| Model | Table | Notes |
|-------|-------|-------|
| `User` | `users` | Email/username optional; supports anonymous users |
| `PracticeSession` | `sessions` | Status: active / completed / abandoned |
| `Transcript` | `transcripts` | JSONB timestamps + future pronunciation_data |
| `FluencyMetrics` | `fluency_metrics` | Snapshot of analyzer output |
| `Conversation` | `conversations` | role + content turns |

UUIDs are stored as strings (`UUID(as_uuid=False)`) for simple JSON APIs.

### Session dependency

`get_db` yields an `AsyncSession`, commits on success, rolls back on error. Services `flush()` / `refresh()`; they do not commit independently — keeping unit-of-work at the request boundary.

### Migrations

```bash
alembic upgrade head
```

Initial revision: `001_initial_schema.py` creates all tables and indexes.

---

## 11. Error Handling

Registered in `middleware/exception_handler.py`:

| Exception | HTTP | Meaning |
|-----------|------|---------|
| `AudioValidationError` | 400 / 413 | Missing, empty, wrong type, too large |
| `RequestValidationError` | 422 | Bad JSON / form fields |
| `GroqAPIError` | 502 / 503 / 504 | Upstream AI failures |
| `SessionNotFoundError` | 404 | Unknown session id |
| `SQLAlchemyError` | 500 | DB failures (message sanitized) |
| unhandled `Exception` | 500 | Last-resort safety net |

Responses include `detail` and often `error_code` for the frontend.

---

## 12. Logging

- `setup_logging()` configures a stdout formatter.
- `RequestLoggingMiddleware` logs inbound method/path and outbound status + ms.
- Services log significant AI/DB actions at INFO; failures at ERROR with context.

Response header `X-Process-Time-Ms` helps the frontend and load tests measure latency.

---

## 13. Security Considerations

| Topic | Current posture |
|-------|-----------------|
| Secrets | Env-only via Settings |
| CORS | Explicit allowlist |
| Uploads | Extension + size checks |
| Auth | JWT helpers ready; routes return 501 |
| Passwords | bcrypt via passlib (for future register) |
| Error leakage | DB/internal errors do not dump stack traces to clients |

Before production: rotate `SECRET_KEY`, restrict CORS, terminate TLS at the edge, rate-limit `/speech/transcribe` and `/chat`, and require auth for session history.

---

## 14. Future Scalability

Designed extension points:

| Feature | Hook |
|---------|------|
| JWT / OAuth | `core/security.py` + replace auth route stubs |
| Pronunciation | `Transcript.pronunciation_data` / response field |
| Redis | Cache session summaries / rate limits |
| Celery | Offload long transcription jobs; return job ids |
| WebSockets / SSE | Stream Llama tokens from a dedicated route |
| Piper | Implement `PiperTTSProvider.synthesize` |
| Docker / K8s | Package `uvicorn app.main:app`; run Alembic init container |

Horizontal scale: stateless API pods + managed Postgres. Sticky sessions are unnecessary if session state lives in the DB.

---

## 15. Deployment Considerations

1. Build image from `backend/` with Python 3.12.  
2. Inject env vars (never bake `.env` into the image).  
3. Run `alembic upgrade head` before serving traffic.  
4. Start: `uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers N`.  
5. Health check: `GET /api/health`.  
6. Put a reverse proxy (nginx / Traefik / cloud LB) in front for TLS.  
7. Monitor Groq latency and 5xx rates separately from app errors.

---

## 16. Local Development Checklist

```bash
cd backend
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # set GROQ_API_KEY + DATABASE_URL
alembic upgrade head
uvicorn app.main:app --reload
pytest -q
```

---

## 17. Production Standards Checklist

This backend follows common production practices:

- [x] Layered architecture (API → service → infra)  
- [x] Async I/O for HTTP and DB  
- [x] Typed interfaces and Pydantic contracts  
- [x] Central config and secrets handling  
- [x] Migration-managed schema  
- [x] Structured error codes  
- [x] Request logging with timings  
- [x] Dependency injection for services  
- [x] Strategy pattern for ML/TTS swap-outs  
- [x] Automated tests for health, validation, fluency  
- [x] README + architecture docs for onboarding  

Together with the React frontend, this forms a maintainable foundation for an AI speaking-coach SaaS rather than a disposable demo.
