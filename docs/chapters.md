
# Chapters API

Base URL (local): `http://localhost:8787`

These endpoints manage chapter creation, retrieval, translation, relinking, updates, and deletion.

---

## Create Chapter

### `POST /novels/{novel_id}/chapters`

Creates a chapter and inserts it into the novel’s doubly-linked list using `chapter_no` ordering.

**Body** (`ChapterCreate`)
```json
{
  "chapter_no": 1,
  "title": "optional",
  "raw": "untranslated text",
  "content": "optional pretranslated",
  "source_url": "https://example.com/chapter/1"
}

Responses
	•	200 OK ? ChapterOut
	•	404 Not Found ? {"detail":"Novel not found"}
	•	409 Conflict ? {"detail":"Chapter number already exists for this novel"}

Example

curl -s -X POST http://localhost:8787/novels/2/chapters \
  -H "Content-Type: application/json" \
  -d '{"chapter_no":1,"raw":"?? ??? ??? ????.","source_url":"https://..."}' | jq


?

List Chapters

GET /novels/{novel_id}/chapters

Lists chapters for a novel.

Query params
	•	limit (int, default 500)
	•	offset (int, default 0)

Response
	•	200 OK ? list[ChapterListItem]
	•	404 Not Found ? {"detail":"Novel not found"}

Example

curl -s "http://localhost:8787/novels/2/chapters?limit=500&offset=0" | jq


?

Get Chapter by Chapter Number

GET /novels/{novel_id}/chapters/{chapter_no}

Fetches a chapter by chapter_no within a novel.

Responses
	•	200 OK ? ChapterOut
	•	404 Not Found ? {"detail":"Novel not found"} or {"detail":"Chapter not found"}

Example

curl -s http://localhost:8787/novels/2/chapters/1 | jq


?

Update Chapter

PATCH /chapters/{chapter_id}

Partially updates a chapter.

Body (ChapterUpdate)
Any subset of:
	•	title
	•	raw
	•	content
	•	source_url
	•	status

Responses
	•	200 OK ? ChapterOut
	•	404 Not Found ? {"detail":"Chapter not found"}

Example

curl -s -X PATCH http://localhost:8787/chapters/4 \
  -H "Content-Type: application/json" \
  -d '{"title":"Episode 1","status":"translated"}' | jq


?

Translate Chapter

POST /chapters/{chapter_id}/translate

Translates raw ? content using OpenAI and the parent novel’s context_json (consistency memory).

Responses
	•	200 OK ? ChapterOut
	•	404 Not Found ? {"detail":"Chapter not found"}
	•	400 Bad Request ? {"detail":"..."}
	•	500 Internal Server Error ? {"detail":"..."}
	•	(Occurs if OpenAI errors or unexpected failure)

Example

curl -s -X POST http://localhost:8787/chapters/4/translate | jq


?

Rebuild Linked List Pointers

POST /novels/{novel_id}/chapters/rebuild-links

Rebuilds prev_chapter_id / next_chapter_id for all chapters of a novel using chapter_no ordering.

Use this if links ever get corrupted.

Responses
	•	200 OK ? {"ok": true, "count": <int>}
	•	404 Not Found ? {"detail":"Novel not found"}

Example

curl -s -X POST http://localhost:8787/novels/2/chapters/rebuild-links | jq


?

Delete Chapter (global)

DELETE /chapters/{chapter_id}

Deletes a chapter by DB id and relinks neighbors to keep the doubly-linked list consistent.

Query params
	•	rebuild (bool, default false)
	•	If true, rebuilds all links by chapter_no after deletion.

Responses
	•	200 OK ? ChapterOut (the deleted chapter record)
	•	404 Not Found ? {"detail":"Chapter not found"} (or your service message)

Example

curl -s -X DELETE "http://localhost:8787/chapters/12?rebuild=true" | jq


?

Delete Chapter (scoped to novel)

DELETE /novels/{novel_id}/chapters/{chapter_id}

Same as the global delete, but verifies the chapter belongs to the given novel.

Query params
	•	rebuild (bool, default false)

Responses
	•	200 OK ? ChapterOut
	•	404 Not Found ? {"detail":"Novel not found"} or {"detail":"Chapter not found for this novel"}

Example

curl -s -X DELETE "http://localhost:8787/novels/2/chapters/12" | jq


?

Notes
	•	chapter_no is canonical ordering. The prev_chapter_id/next_chapter_id pointers are derived from it.
	•	The create endpoint inserts the new chapter into the list by finding neighbors via chapter_no.
	•	If you manually edit chapter numbers or pointers, use rebuild-links.

