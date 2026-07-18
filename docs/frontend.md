# SpeakFlow Frontend Documentation

This document describes the React frontend for **SpeakFlow**, an AI English Speaking Coach. It is written so a new developer can understand the UI architecture without reading every source file.

---

## 1. Overview

The frontend is a Vite + React SPA that presents:

1. A **marketing landing page** (`/`) introducing SpeakFlow.
2. A **Practice studio** (`/practice`) where learners speak, see transcripts, review AI replies, and view fluency-style stats.

Today the Practice page uses local mock state to simulate Listening → Thinking → Speaking. The backend APIs (`/api/speech/transcribe`, `/api/chat`, `/api/fluency/analyze`, `/api/session/*`) are designed to plug into this flow next.

**Stack:** React 18, React Router 7, Vite 4, Tailwind CSS 3, Framer Motion, React Icons, Three.js / R3F (available; visualizer currently CSS/Framer-based).

---

## 2. Folder Structure

```
frontend/
├── index.html
├── package.json
├── vite.config.js
├── tailwind.config.js
├── postcss.config.js
└── src/
    ├── main.jsx                 # React root + ThemeProvider
    ├── App.jsx                  # Router shell
    ├── index.css                # Tailwind entry + global tokens
    ├── styles/
    │   └── app.css              # Shared app-level styles (legacy / shared)
    ├── context/
    │   └── ThemeContext.jsx     # Dark/light theme state
    ├── pages/
    │   ├── Landing.jsx          # Marketing page
    │   └── Practice.jsx         # Speaking studio
    └── components/
        ├── Navbar.jsx
        ├── Footer.jsx
        ├── Features.jsx
        ├── Hero.jsx / Hero/     # Earlier single-screen hero (Web Speech API)
        ├── Mic/                 # Microphone control + CSS
        ├── ThemeToggle/         # Theme switch UI
        ├── Background/          # Decorative background
        ├── SpeechVisualizer.jsx # Stub → future Three.js / canvas viz
        ├── TranscriptBox.jsx    # Stub → reusable transcript panel
        ├── Timeline.jsx         # Stub → word timeline
        ├── SidebarStats.jsx     # Stub → fluency sidebar
        └── ControlBar.jsx       # Stub → mic / stop / clear controls
```

### Why each folder exists

| Folder | Purpose |
|--------|---------|
| `pages/` | Route-level screens. Keeps navigation concerns out of presentational components. |
| `components/` | Reusable UI pieces. Feature folders (`Mic/`, `Hero/`) colocate CSS with JSX when styles are component-specific. |
| `context/` | Cross-cutting React context (theme today; session/API client later). |
| `styles/` | Global or multi-page CSS that does not belong to one component. |

Stub components (`SpeechVisualizer`, `TranscriptBox`, etc.) exist as named seams so Practice can be refactored from an inline layout into a composed hierarchy without renaming imports across the app.

---

## 3. Component Hierarchy

```
main.jsx
└── ThemeProvider
    └── App (BrowserRouter)
        ├── Route "/" → Landing
        │     ├── Nav (inline)
        │     ├── Hero section (headline + CTA + visual)
        │     ├── Features grid
        │     ├── How-it-works steps
        │     └── Footer
        │
        └── Route "/practice" → Practice
              ├── Top bar (brand + settings)
              ├── VisualizerGlow (speech state orb)
              ├── Stats sidebar (session time, WPM, fluency)
              ├── Transcript panel ("Your Speech")
              ├── AI response panel
              └── Control buttons (Mic, Stop, Replay, Clear, Settings)
```

**Legacy path:** `components/Hero/Hero.jsx` + `Mic` implement an earlier Web Speech API prototype (browser STT + local “correction”). The product direction is Practice + backend Whisper/Llama; Hero remains useful reference for mic UX and audio-level metering.

---

## 4. Routing

Defined in `App.jsx`:

| Path | Page | Role |
|------|------|------|
| `/` | `Landing` | Acquisition / explanation |
| `/practice` | `Practice` | Core product loop |

Navigation uses `react-router-dom` (`Link`, `BrowserRouter`, `Routes`, `Route`). Landing CTAs deep-link to `/practice`.

```
User opens site
      │
      ▼
   Landing (/)
      │  "Start Practicing"
      ▼
   Practice (/practice)
      │
      ▼
   (future) API calls → SpeakFlow backend
```

---

## 5. State Management Approach

**Current approach: local React state**

- `Practice.jsx` owns `isRecording`, `state` (`Idle` \| `Listening` \| `Thinking` \| `Speaking`), `transcript`, `response`, and `level`.
- `ThemeContext` holds theme in `localStorage` and sets `data-theme` on `document.body`.

**Why not Redux/Zustand yet?**

The UI is still largely presentational with mocked AI turns. Introducing a global store before the API contract is wired would create churn.

**Recommended next step**

```
PracticePage
   │
   ├── usePracticeSession()     # session start/end, ids
   ├── useTranscription()       # MediaRecorder → POST /speech/transcribe
   ├── useCoachChat()           # POST /chat
   └── useFluency()             # POST /fluency/analyze → sidebar stats
```

Custom hooks keep components thin and match the backend service boundaries.

---

## 6. UI Architecture

### Design language

- Dark zinc canvas (`#09090B`) with blue/violet accents (`#3B82F6`, `#8B5CF6`).
- Soft glass panels: `border-white/10`, translucent `bg-white/5`.
- Large rounded sections (`rounded-[2rem]`) for a “studio” feel.
- Brand name **SpeakFlow** appears in nav and practice chrome.

### Page responsibilities

| Page | One job |
|------|---------|
| Landing | Explain value and convert to Practice |
| Practice | Run one speaking loop and show feedback |

Landing sections are intentionally separated: hero → features → how it works → footer.

---

## 7. Tailwind Organization

Configured in `tailwind.config.js`:

```js
colors: {
  background: '#09090B',
  card: '#18181B',
  accent: '#3B82F6',
  accentSecondary: '#8B5CF6',
  text: '#F4F4F5',
}
boxShadow: {
  glow: '0 0 0 1px rgba(59,130,246,0.2), 0 0 40px rgba(59,130,246,0.15)',
}
```

`index.css` imports Tailwind layers and sets global Inter font + dark page background.

**Conventions**

- Prefer utility classes in JSX for layout and color.
- Use component CSS modules/files (`Mic.css`, `Hero.css`) only when animation or complex selectors are awkward in utilities.
- Semantic tokens (`bg-background`, `text-accent`) over raw hex in new code.

---

## 8. Animation Strategy

**Framer Motion** drives intentional motion:

| Surface | Motion | Intent |
|---------|--------|--------|
| Landing hero | Fade / slide-in | Presence on first paint |
| Feature cards | `whileInView` stagger | Progressive reveal |
| Practice panels | Opacity + Y translate | Soft entrance |
| VisualizerGlow | Scale pulse + bar heights | Map `Listening` / `Thinking` / `Speaking` to life |

Avoid random perpetual motion on static marketing copy. Motion should reinforce state (listening vs idle), not decorate every box.

---

## 9. Three.js Speech Visualizer

Dependencies `@react-three/fiber`, `@react-three/drei`, and `three` are installed for a WebGL visualizer.

**Current status:** `SpeechVisualizer.jsx` is a stub (`return null`). Practice uses `VisualizerGlow` (CSS + Framer) as a lightweight stand-in.

**Intended architecture**

```
SpeechVisualizer
   ├── Canvas (R3F)
   │     ├── Ambient / point lights
   │     ├── Particle or shader mesh driven by audio level
   │     └── Optional drei helpers (OrbitControls off for product UI)
   └── props: { state, level, isRecording }
```

Feed `level` from `AnalyserNode` (Web Audio) once MediaRecorder is connected. Keep the Three.js canvas behind a feature flag until performance is validated on mid-tier devices.

---

## 10. Transcript Components

| Component | Role |
|-----------|------|
| Inline panels in `Practice.jsx` | Current “Your Speech” / “AI Response” |
| `TranscriptBox.jsx` | Future shared transcript view (scroll, live badge, copy) |
| `Timeline.jsx` | Future word-level highlight from Whisper timestamps |

Backend returns:

```json
{
  "transcript": "...",
  "timestamps": [{ "word": "hello", "start": 0.0, "end": 0.4 }],
  "duration": 1.2
}
```

The Timeline can scrub or highlight words using `start` / `end`. Fluency filler words can be highlighted in the transcript by matching against `/api/fluency/analyze` results.

---

## 11. Responsive Design

- Landing: single column on mobile; two-column hero on `lg`.
- Practice: visualizer stacks above stats on small screens; side-by-side on `lg`.
- Control bar uses `flex-wrap` so buttons reflow.
- Horizontal padding via `px-6 lg:px-8` and `max-w-7xl` containers.

Test at ~375px, ~768px, and ≥1280px when changing Practice layout.

---

## 12. Audio & Mic UX (current + target)

**Legacy Hero:** Web Speech API + `AudioContext` for level metering.

**Target Practice loop**

```
User taps Mic
   │
   ▼
MediaRecorder captures audio blob
   │
   ▼
POST /api/speech/transcribe
   │
   ├── show transcript + timestamps
   ├── POST /api/fluency/analyze → sidebar
   └── POST /api/chat → AI response
         │
         ▼ (future)
      TTS / Piper playback → state = Speaking
```

Session lifecycle should call `POST /api/session/start` when entering Practice and `POST /api/session/end` on leave/stop.

---

## 13. Best Practices Followed

- Route-level code splitting by page components.
- Context only for true cross-cutting concerns (theme).
- Named stub components as extension points.
- Tailwind design tokens for brand consistency.
- Motion tied to product states, not decorative noise.
- Accessibility direction: keep button labels textual (`Microphone`, `Stop`); prefer visible focus rings when polishing.

---

## 14. Future Improvements

1. Wire Practice to the FastAPI backend (fetch / axios / ky client module).
2. Replace mock timeouts with real STT → chat → fluency pipeline.
3. Implement `SpeechVisualizer` with R3F driven by Web Audio levels.
4. Extract `TranscriptBox`, `SidebarStats`, `ControlBar` from Practice.
5. Persist theme + last session id; add auth-aware nav when JWT lands.
6. Streaming chat (SSE/WebSocket) for token-by-token coach replies.
7. Pronunciation overlays once `pronunciation_data` is populated by the backend.

---

## 15. Quick Start

```bash
cd frontend
npm install
npm run dev
```

Open the Vite URL (typically `http://localhost:5173`). For full AI features, run the backend on port 8000 and configure CORS / proxy accordingly.
