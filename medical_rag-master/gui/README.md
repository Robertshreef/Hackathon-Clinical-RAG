# Stacks — RAG Chat UI

A React front end for your FastAPI RAG backend (`auth_router` + `chat_router`).
Claude/ChatGPT-style layout — conversation sidebar, chat thread, streaming-style
message bubbles — plus a dedicated **references rail** on the right that turns
each `CitedSource` your `/chat/conversations/{id}/messages` endpoint returns
into its own expandable card, linked to inline `[n]` markers in the answer text.

## Structure

```
src/
  lib/api.js            fetch client: auth headers, silent token refresh, all endpoints
  lib/citations.js       splits "answer text [1] more text [2]" into renderable tokens
  context/AuthContext.jsx  login/register/logout/me, session state
  components/
    LoginScreen.jsx       sign in / register
    Sidebar.jsx            conversation list: create, rename, delete
    ChatView.jsx           message list + input + wires up the rail
    MessageBubble.jsx      renders one turn; assistant turns get clickable [n] markers
    ChatInput.jsx          autosizing composer
    CitationsRail.jsx      collapsible panel, one CitationCard per source
    CitationCard.jsx       single reference: file name, page range, expandable reason
```

## Setup

```bash
npm install
cp .env.example .env      # set VITE_API_BASE_URL to your FastAPI server
npm run dev
```

## Wiring notes specific to your backend

- **Auth**: `POST /auth/login` returns `{access_token, refresh_token}`, both
  stored in `localStorage`. Every request attaches
  `Authorization: Bearer <access_token>`. On a 401, the client calls
  `POST /auth/refresh` once and retries the original request; if that also
  fails, the user is dropped back to the login screen.
- **Sending a message**: your `send_message` endpoint takes `query: str` as a
  plain (non-Pydantic) parameter, so FastAPI binds it as a **query string**
  parameter, not a JSON body. `chatApi.sendMessage` sends it as
  `?query=...` accordingly — if you later change the endpoint to accept a
  Pydantic body, update that one call in `src/lib/api.js`.
- **References**: `ChatResponse.sources` is a `list[CitedSource]` with
  `index`, `reason`, `file_name`, `starting_page`, `end_page`. The UI expects
  your agent's answer text to contain matching `[index]` markers inline
  (e.g. `"...as shown in the appendix [1]."`) so they can be turned into
  clickable superscripts. If your agent doesn't emit those markers today,
  the reference cards still render in the rail — inline linking just won't
  connect until the markers are present.
- **History has no sources**: `GET /messages` only returns `role`/`content`
  (per `MessageMetadata`), so the references rail is populated from the most
  recent `send_message` response only, and clears when you switch
  conversations. If you want sources persisted across reloads, you'll need to
  either store them server-side per message or extend `MessageMetadata`.

## New: voice input

`ChatInput` uses the browser's native `SpeechRecognition` API — no extra
dependency. Click the mic to dictate; recognized speech is appended into the
composer live. It's Chrome/Edge/Safari only (not supported in Firefox); the
mic button simply doesn't render if `window.SpeechRecognition` /
`window.webkitSpeechRecognition` aren't present, so nothing breaks on
unsupported browsers. Requires the page to be served over `https://` or
`localhost` — browsers block mic access on plain `http://` origins.

## New: downloading reference files

Each `CitedSource` card in the rail now has a download button next to its
file name. This needs one addition on the backend, since nothing currently
serves `medical_rag/data/src/*` to the frontend:

**`backend-snippet-download-endpoint.py`** (included in this zip) — copy its
contents into `medical_rag/app/modules/chat/router.py`. It adds
`GET /chat/files/{file_name}`, which:
- requires a valid access token (same `get_current_user` dependency as the
  rest of the chat routes), so source documents aren't publicly downloadable
- resolves `file_name` against `medical_rag/data/src` and rejects anything
  that resolves outside that directory (blocks `../` path traversal)
- streams the file back with `FileResponse`

The snippet assumes `router.py` lives at `medical_rag/app/modules/chat/router.py`
and data at `medical_rag/data/src` — hence `parents[3]`. If your `gui` folder
being at `medical_rag/gui` means the actual backend path differs, adjust
`DATA_DIR` accordingly; it's just `Path(__file__).resolve().parents[N] / "data" / "src"`
for whichever `N` lands you at `medical_rag/`.

On the frontend, `chatApi.downloadFile(fileName)` in `src/lib/api.js` fetches
that endpoint with the auth header attached (same silent-refresh-on-401
behavior as every other request), then triggers a normal browser save-as —
no page navigation, no extra auth prompt.

## CORS (required — you'll hit this immediately)

Your `app/main.py` doesn't currently add `CORSMiddleware`. If the frontend
runs on a different origin than the API (it will, in dev — Vite on `:5173`
vs FastAPI on `:8000`), add this in `main.py`:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # your frontend origin(s)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Design

Deliberately not another cream/terracotta or dark/neon AI-chat template: a
"reading room" palette (deep ink navy, parchment, muted gold) with Fraunces
for display type and inline citation markers styled like catalog tabs, since
the whole point of the UI is grounding answers in cited pages.
