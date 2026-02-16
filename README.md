# Novel Chrome Extension + Backend

A personal pipeline for:
- Extracting chapter text from supported sites via a Chrome extension hotkey
- Storing raw + translated chapters in Postgres
- Translating with OpenAI while maintaining per-novel consistency ("context memory")
- Eventually reading/managing chapters from a dedicated frontend

## Repo Layout

```
- backend/     # FastAPI + SQLAlchemy + Alembic + Postgres (Dockerized)
- extension/   # Chrome extension (hotkey -> extract -> POST -> translate)
```

## Features

### Backend
- FastAPI REST API
- Postgres storage (Docker)
- Alembic migrations
- Models:
  - Novel: name, languages, context_json (translation consistency memory)
  - Chapter: raw + content, status, chapter_no, prev/next pointers (doubly linked list)
  - ReadingProgress + Bookmark (for future reader)

### Extension
- One hotkey to:
  1. Extract text from the current tab (site-specific extractor config)
  2. Post it as a chapter to the backend
  3. Trigger translation
- Per-site extractor configs saved in chrome.storage.local
- CSP-safe extraction (no eval / new Function)

### Prerequisites
- Docker + Docker Compose
- OpenAI API key
- Chrome/Chromium-based browser (Arc works too)

## Backend: Quick Start

### 1) Configure Environment

Create backend/.env:

```bash
cd backend

cat > .env <<'EOF'
OPENAI_API_KEY=YOUR_KEY_HERE
DATABASE_URL=postgresql+psycopg2://postgres:postgres@db:5432/app
EOF
```

### 2) Start Services

```bash
docker compose up --build
```

API will be available at:

http://localhost:8787

### 3) Run Migrations

```bash
docker compose exec api alembic -c /app/alembic.ini upgrade head
```

### 4) Health Check

```bash
curl -s http://localhost:8787/health | jq
```

## Extension: Quick Start

### 1) Load Unpacked
1. Open chrome://extensions
2. Enable Developer mode
3. Click Load unpacked
4. Select the extension/ folder

### 2) Assign the Hotkey

Go to:

chrome://extensions/shortcuts

Assign the command for the extension (one hotkey).

### 3) Configure Settings on a Chapter Page

Open the extension popup while on the target site and set:
- Backend URL: http://localhost:8787
- Novel ID: the novel you're posting to
- Chapter No: the number to store
- Extractor Config (JSON): per-host extractor config (examples below)

Click Save.

### 4) Press Hotkey

On a chapter page, press the hotkey:
- Toast: extracting
- Toast: posting
- Toast: translating
- Toast: done
- Auto-increment chapter number (if enabled)

## Extractor Configs (JSON)

These are CSP-safe and editable without changing code.

#### Booktoki

```json
{
  "mode": "selector",
  "selector": "#novel_content > div:not(.view-img)",
  "prop": "textContent"
}
```

#### Kakao (Shadow DOM)

```json
{
  "mode": "shadowSelector",
  "shadowSelector": ".DC2CN",
  "prop": "innerText"
}
```

#### Notes
- mode: "selector" uses normal querySelector
- mode: "shadowSelector" searches shadow roots until it finds the first match

## Create a Novel (Example)

```bash
curl -s -X POST http://localhost:8787/novels \
  -H "Content-Type: application/json" \
  -d '{"name":"My Novel","source_lang":"ko","target_lang":"en"}' | jq
```

### Common Checks

#### List Novels

```bash
curl -s http://localhost:8787/novels | jq
```

#### List Chapters for a Novel

```bash
curl -s http://localhost:8787/novels/2/chapters | jq
```

#### Fetch Chapter Content

```bash
curl -s http://localhost:8787/chapters/4 | jq
```

## Context Memory (Consistency)

Each novel stores context_json, which is used to maintain consistency across translations.

This is not a user-managed glossary. It is automatic "consistency memory":
- Canon entities (names, orgs, places, items)
- Locked renderings (recurring phrases/moves)
- Style rules (tone, honorific handling, formatting preferences)

The translation service:
- Sends a bounded slice of context to reduce token usage
- Merges returned context_updates into stored context
- Prunes stored context to prevent unbounded growth

## Development Notes

### If You Kill the Terminal Session

Docker containers continue running unless you stop them:

```bash
docker compose down
```

### Logs

```bash
docker compose logs -f api
docker compose logs -f db
```

## Next Steps

Build a small frontend for:
- Managing novels and chapters
- Reading chapters with prev/next navigation
- Bookmarks + reading progress

## License

Personal/private usage.