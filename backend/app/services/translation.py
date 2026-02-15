from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, cast

from openai import OpenAI
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.chapter import Chapter
from app.models.novel import Novel

client = OpenAI(api_key=settings.OPENAI_API_KEY)

# Context is NOT a glossary.
# It is "consistency memory": canon entities, locked renderings, and style rules.
SYSTEM_PROMPT = """You are a professional literary translator.

You MUST:
1) Translate the input text from source_lang to target_lang.
2) Maintain consistency with the provided context memory (canon entities + locked renderings + style rules).
3) Propose context updates ONLY when you are confident a term/name/phrase is a recurring proper noun, item, skill, faction, place, title, or domain-specific jargon.

Return STRICT JSON with keys:
- "translation": string
- "context_updates": object
No markdown. No extra keys.

context_updates schema:
{
  "locks_add": [{"src": str, "dst": str, "reason": str}],
  "entities_add": [{"type": "person"|"place"|"org"|"item"|"skill"|"title"|"other", "src": str, "dst": str}],
  "style_patch": { ... }  // OPTIONAL: merge patch into context.style
}

Rules:
- NEVER invent new facts.
- If context already locks a src term, you MUST use its dst exactly.
- If you are unsure a term is recurring, do NOT add it.
"""


# --- Context helpers (normalize, merge, prune, slice) -------------------------


def _normalize_context(ctx: dict[str, Any] | None) -> dict[str, Any]:
    ctx = dict(ctx or {})
    ctx.setdefault("version", 1)
    ctx.setdefault("style", {})
    ctx.setdefault("locks", [])  # list[{src,dst,reason,count,last_seen_chapter,...}]
    ctx.setdefault(
        "canon", {}
    )  # dict with "entities": list[{type,src,dst,count,last_seen_chapter,...}]
    cast(dict[str, Any], ctx["canon"]).setdefault("entities", [])
    return ctx


def _deep_merge(dst: dict[str, Any], patch: dict[str, Any]) -> dict[str, Any]:
    for k, v in patch.items():
        if isinstance(v, dict) and isinstance(dst.get(k), dict):
            _deep_merge(cast(dict[str, Any], dst[k]), v)
        else:
            dst[k] = v
    return dst


def _upsert_lock(
    ctx: dict[str, Any],
    *,
    src: str,
    dst: str,
    reason: str,
    chapter_no: int,
) -> None:
    locks: list[dict[str, Any]] = cast(list[dict[str, Any]], ctx.setdefault("locks", []))
    for entry in locks:
        if entry.get("src") == src:
            if entry.get("dst") == dst:
                entry["count"] = int(entry.get("count", 1)) + 1
                entry["last_seen_chapter"] = chapter_no
            else:
                conflicts = entry.setdefault("conflicts", [])
                conflicts.append(
                    {
                        "dst": dst,
                        "reason": reason,
                        "chapter_no": chapter_no,
                        "at": datetime.now(timezone.utc).isoformat(),
                    }
                )
                entry["last_seen_chapter"] = chapter_no
            return

    locks.append(
        {
            "src": src,
            "dst": dst,
            "reason": reason,
            "count": 1,
            "last_seen_chapter": chapter_no,
        }
    )


def _upsert_entity(
    ctx: dict[str, Any],
    *,
    etype: str,
    src: str,
    dst: str,
    chapter_no: int,
) -> None:
    canon = cast(dict[str, Any], ctx.setdefault("canon", {}))
    entities: list[dict[str, Any]] = cast(list[dict[str, Any]], canon.setdefault("entities", []))

    for e in entities:
        if e.get("type") == etype and e.get("src") == src:
            if e.get("dst") == dst:
                e["count"] = int(e.get("count", 1)) + 1
                e["last_seen_chapter"] = chapter_no
            else:
                conflicts = e.setdefault("conflicts", [])
                conflicts.append(
                    {
                        "dst": dst,
                        "chapter_no": chapter_no,
                        "at": datetime.now(timezone.utc).isoformat(),
                    }
                )
                e["last_seen_chapter"] = chapter_no
            return

    entities.append(
        {
            "type": etype,
            "src": src,
            "dst": dst,
            "count": 1,
            "last_seen_chapter": chapter_no,
        }
    )


def merge_context_updates(
    *,
    existing: dict[str, Any] | None,
    updates: dict[str, Any] | None,
    chapter_no: int,
) -> dict[str, Any]:
    ctx = _normalize_context(existing)
    updates = dict(updates or {})

    locks_add = updates.get("locks_add") or []
    if isinstance(locks_add, list):
        for item in locks_add:
            if not isinstance(item, dict):
                continue
            src = item.get("src")
            dst = item.get("dst")
            reason = item.get("reason") or "recurring term"
            if isinstance(src, str) and isinstance(dst, str) and src.strip() and dst.strip():
                _upsert_lock(
                    ctx,
                    src=src.strip(),
                    dst=dst.strip(),
                    reason=str(reason),
                    chapter_no=chapter_no,
                )

    entities_add = updates.get("entities_add") or []
    if isinstance(entities_add, list):
        for item in entities_add:
            if not isinstance(item, dict):
                continue
            etype = item.get("type") or "other"
            src = item.get("src")
            dst = item.get("dst")
            if isinstance(src, str) and isinstance(dst, str) and src.strip() and dst.strip():
                _upsert_entity(
                    ctx,
                    etype=str(etype),
                    src=src.strip(),
                    dst=dst.strip(),
                    chapter_no=chapter_no,
                )

    style_patch = updates.get("style_patch")
    if isinstance(style_patch, dict):
        style = cast(dict[str, Any], ctx.setdefault("style", {}))
        _deep_merge(style, cast(dict[str, Any], style_patch))

    ctx["updated_at"] = datetime.now(timezone.utc).isoformat()
    return ctx


def build_context_slice(
    ctx: dict[str, Any],
    *,
    chapter_no: int,
    raw_text: str,
    recent_window: int = 50,
    min_count: int = 3,
    max_locks: int = 200,
    max_entities: int = 300,
) -> dict[str, Any]:
    """
    Build a bounded "slice" of context to send to the model to reduce token cost.
    Prioritizes:
      - matches present in raw_text
      - recent items (last_seen within window)
      - frequent items (count)
    """
    ctx = _normalize_context(ctx)
    raw = raw_text or ""

    def score(entry: dict[str, Any]) -> tuple[int, int, int]:
        src = str(entry.get("src", ""))
        is_match = 1 if (src and src in raw) else 0
        last_seen = int(entry.get("last_seen_chapter") or 0)
        recency = max(0, recent_window - (chapter_no - last_seen))
        count = int(entry.get("count") or 0)
        return (is_match, recency, count)

    locks = [e for e in (ctx.get("locks") or []) if isinstance(e, dict)]
    locks = [
        e
        for e in locks
        if int(e.get("count") or 0) >= min_count
        or (chapter_no - int(e.get("last_seen_chapter") or 0)) <= recent_window
    ]
    locks.sort(key=score, reverse=True)
    locks = locks[:max_locks]

    entities = [e for e in (ctx.get("canon", {}).get("entities") or []) if isinstance(e, dict)]
    entities = [
        e
        for e in entities
        if int(e.get("count") or 0) >= min_count
        or (chapter_no - int(e.get("last_seen_chapter") or 0)) <= recent_window
    ]
    entities.sort(key=score, reverse=True)
    entities = entities[:max_entities]

    return {
        "version": ctx.get("version", 1),
        "style": ctx.get("style", {}),
        "locks": locks,
        "canon": {"entities": entities},
    }


def prune_context_in_db(
    ctx: dict[str, Any],
    *,
    current_chapter_no: int,
    keep_recent_window: int = 200,
    min_count_keep: int = 2,
    max_locks: int = 1000,
    max_entities: int = 1500,
) -> dict[str, Any]:
    """
    Hard-prune stored DB context so it doesn't grow forever.
    Separate from the (smaller) slice sent to the model.
    """
    ctx = _normalize_context(ctx)

    def keep(e: dict[str, Any]) -> bool:
        last_seen = int(e.get("last_seen_chapter") or 0)
        count = int(e.get("count") or 0)
        return (count >= min_count_keep) or ((current_chapter_no - last_seen) <= keep_recent_window)

    locks = [e for e in (ctx.get("locks") or []) if isinstance(e, dict) and keep(e)]
    locks.sort(
        key=lambda e: (int(e.get("count") or 0), int(e.get("last_seen_chapter") or 0)),
        reverse=True,
    )
    ctx["locks"] = locks[:max_locks]

    canon = cast(dict[str, Any], ctx.setdefault("canon", {}))
    entities = [e for e in (canon.get("entities") or []) if isinstance(e, dict) and keep(e)]
    entities.sort(
        key=lambda e: (int(e.get("count") or 0), int(e.get("last_seen_chapter") or 0)),
        reverse=True,
    )
    canon["entities"] = entities[:max_entities]

    return ctx


# --- OpenAI call + chapter translate ------------------------------------------


def translate_text_with_context(
    *,
    novel_id: int,
    source_lang: str,
    target_lang: str,
    text: str,
    context: dict[str, Any],
) -> dict[str, Any]:
    payload = {
        "novel_id": novel_id,
        "source_lang": source_lang,
        "target_lang": target_lang,
        "text": text,
        "context_memory": context or {},
        "constraints": [
            "Follow context_memory.locks and context_memory.canon.entities exactly when they match.",
            "Propose updates only for recurring names/items/skills/factions/places/titles/jargon.",
            "Do not add common words.",
        ],
    }

    resp = client.chat.completions.create(
        model="gpt-4.1-mini",
        temperature=0.2,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
        ],
        response_format={"type": "json_object"},
    )

    data = json.loads(resp.choices[0].message.content)
    if not isinstance(data, dict):
        raise ValueError("Model returned non-object JSON")
    return cast(dict[str, Any], data)


def translate_chapter(
    db: Session,
    *,
    novel_id: int,
    chapter_id: int,
) -> Chapter:
    """
    Translates Chapter.raw -> Chapter.content using Novel.context_json "consistency memory",
    merges returned context_updates into Novel.context_json, and prunes it.
    """
    novel = db.get(Novel, novel_id)
    if not novel:
        raise ValueError("Novel not found")

    chapter = db.get(Chapter, chapter_id)
    if not chapter or chapter.novel_id != novel_id:
        raise ValueError("Chapter not found for this novel")

    if not chapter.raw or not chapter.raw.strip():
        raise ValueError("Chapter has no raw text to translate")

    existing_ctx = _normalize_context(novel.context_json or {})

    # Send only a bounded slice to reduce token cost
    context_slice = build_context_slice(
        existing_ctx,
        chapter_no=int(chapter.chapter_no),
        raw_text=chapter.raw,
    )

    result = translate_text_with_context(
        novel_id=novel.id,
        source_lang=novel.source_lang,
        target_lang=novel.target_lang,
        text=chapter.raw,
        context=context_slice,
    )

    translation = result.get("translation")
    context_updates = result.get("context_updates")

    if not isinstance(translation, str):
        raise ValueError("Model returned invalid schema: translation must be string")
    if context_updates is not None and not isinstance(context_updates, dict):
        raise ValueError("Model returned invalid schema: context_updates must be object")

    chapter.content = translation
    chapter.status = "translated"
    chapter.translated_at = datetime.now(timezone.utc)

    merged = merge_context_updates(
        existing=existing_ctx,
        updates=cast(dict[str, Any] | None, context_updates),
        chapter_no=int(chapter.chapter_no),
    )

    novel.context_json = prune_context_in_db(
        merged,
        current_chapter_no=int(chapter.chapter_no),
    )

    db.flush()
    return chapter
