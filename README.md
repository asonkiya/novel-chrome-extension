# Novel Chrome Extension + Backend

A personal pipeline for:
- extracting chapter text from supported sites via a Chrome extension hotkey
- storing raw + translated chapters in Postgres
- translating with OpenAI while maintaining per-novel consistency (“context memory”)
- eventually reading/managing chapters from a dedicated frontend

Repo layout:

.
??? backend/      # FastAPI + SQLAlchemy + Alembic + Postgres (Dockerized)
??? extension/    # Chrome extension (hotkey -> extract -> POST -> translate)

---

## Features

### Backend
- FastAPI REST API
- Postgres storage (Docker)
- Alembic migrations
- Models:
  - **Novel**: name, langs, `context_json` (translation consistency memory)
  - **Chapter**: raw + content, status, chapter_no, prev/next pointers (doubly linked list)
  - **ReadingProgress** + **Bookmark** (for future reader)

### Extension
- One hotkey to:
  1) extract text from the current tab (site-specific extractor config)
  2) post it as a chapter to the backend
  3) trigger translation
- Per-site extractor configs saved in `chrome.storage.local`
- CSP-safe extraction (no `eval` / `new Function`)

---

## Prereqs
- Docker + Docker Compose
- OpenAI API key
- Chrome/Chromium-based browser (Arc works too)

---

## Backend: Quick Start

### 1) Configure environment
Create `backend/.env`:

```bash
cd backend
cat > .env <<'EOF'
OPENAI_API_KEY=YOUR_KEY_HERE
DATABASE_URL=postgresql+psycopg2://postgres:postgres@db:5432/app
EOF

2) Start services

docker compose up --build

API will be available at: http://localhost:8787

3) Run migrations

docker compose exec api alembic -c /app/alembic.ini upgrade head

4) Health check

curl -s http://localhost:8787/health | jq


?

Extension: Quick Start

1) Load unpacked
	1.	Open chrome://extensions
	2.	Enable Developer mode
	3.	Click Load unpacked
	4.	Select the extension/ folder

2) Assign the hotkey

Go to: chrome://extensions/shortcuts
Assign the command for the extension (one hotkey).

3) Configure settings on a chapter page

Open the extension popup while on the target site and set:
	•	Backend URL: http://localhost:8787
	•	Novel ID: the novel you’re posting to
	•	Chapter No: the number to store
	•	Extractor Config (JSON): per-host extractor config (examples below)

Click Save.

4) Press hotkey

On a chapter page, press the hotkey:
	•	toast: extracting
	•	toast: posting
	•	toast: translating
	•	toast: done (+ auto-increment chapter no if enabled)

?

Extractor Configs (JSON)

These are CSP-safe and editable without changing code.

Booktoki

{"mode":"selector","selector":"#novel_content > div:not(.view-img)","prop":"textContent"}

Kakao (Shadow DOM)

{"mode":"shadowSelector","shadowSelector":".DC2CN","prop":"innerText"}

Notes:
	•	mode: "selector" uses normal DOM querySelector
	•	mode: "shadowSelector" searches shadow roots until it finds the first match

?

Create a novel (example)

curl -s -X POST http://localhost:8787/novels \
  -H "Content-Type: application/json" \
  -d '{"name":"My Novel","source_lang":"ko","target_lang":"en"}' | jq


?

Common checks

List novels

curl -s http://localhost:8787/novels | jq

List chapters for a novel

curl -s http://localhost:8787/novels/2/chapters | jq

Fetch chapter content

curl -s http://localhost:8787/chapters/4 | jq


?

Context Memory (Consistency)

Each novel stores context_json, which is used to maintain consistency across translations.

It is not a user-managed glossary. It’s automatic “consistency memory”:
	•	canon entities (names, orgs, places, items)
	•	locked renderings (recurring phrases/moves)
	•	style rules (tone, honorific handling, formatting preferences)

The translation service:
	•	sends a bounded “slice” of context to reduce token usage
	•	merges returned context_updates into stored context
	•	prunes stored context to prevent unbounded growth

?

Development Notes

If you kill the terminal session

Docker containers continue running unless you stop them:

docker compose down

Logs

docker compose logs -f api
docker compose logs -f db


?

Next Steps
		Build a small frontend for:
		managing novels and chapters
		reading chapters with prev/next navigation
		bookmarks + reading progress

?

License

Personal/private usage.

