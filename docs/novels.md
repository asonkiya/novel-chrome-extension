
# Novels API

All novel endpoints are under `/novels`.

Base URL (local): `http://localhost:8787`

---

## Create Novel

### `POST /novels`

Creates a new novel.

**Body** (`NovelCreate`)
```json
{
  "name": "My Novel",
  "source_lang": "ko",
  "target_lang": "en"
}

Responses
	•	200 OK ? NovelOut
	•	409 Conflict ? {"detail":"Novel with this name already exists"}

Example

curl -s -X POST http://localhost:8787/novels \
  -H "Content-Type: application/json" \
  -d '{"name":"My Novel","source_lang":"ko","target_lang":"en"}' | jq


?

List Novels

GET /novels

Lists novels.

Query params
	•	limit (int, default 100)
	•	offset (int, default 0)

Responses
	•	200 OK ? list[NovelOut]

Example

curl -s "http://localhost:8787/novels?limit=100&offset=0" | jq


?

Get Novel

GET /novels/{novel_id}

Fetch a single novel by id.

Responses
	•	200 OK ? NovelOut
	•	404 Not Found ? {"detail":"Novel not found"}

Example

curl -s http://localhost:8787/novels/2 | jq


?

Get Novel Context

GET /novels/{novel_id}/context

Returns the novel’s context_json only.

Responses
	•	200 OK ? object (context JSON)
	•	404 Not Found ? {"detail":"Novel not found"}

Example

curl -s http://localhost:8787/novels/2/context | jq


?

Replace Novel Context

PUT /novels/{novel_id}/context

Replaces (overwrites) the novel’s stored context_json.

Body (NovelContextUpdate)

{
  "context_json": {}
}

Responses
	•	200 OK ? {"ok": true}
	•	404 Not Found ? {"detail":"Novel not found"}

Example

curl -s -X PUT http://localhost:8787/novels/2/context \
  -H "Content-Type: application/json" \
  -d '{"context_json":{"style":{"tone":"light novel"}}}' | jq


?

Notes
	•	context_json is per-novel “consistency memory” used during translation (canon entities, locked renderings, style rules).
	•	Chapter creation and reading endpoints live under the Chapters API (see chapters.md).

