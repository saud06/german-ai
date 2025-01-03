from __future__ import annotations
from typing import List, Optional, Dict, Any
import json

from .config import settings


async def generate_questions(track: Optional[str], size: int, level: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Try to generate `size` quiz questions for a given `track` (skill) and CEFR `level`.
    Returns a list of questions with fields: id, type, question/sentence, options, answer, skills.
    If no AI key is configured or generation fails, returns an empty list.
    """
    if not settings.OPENAI_API_KEY:
        return []

    try:
        # Lazy import so the package is optional
        try:
            from openai import OpenAI
        except Exception:
            # If SDK is not installed, skip generation gracefully
            return []

        client = OpenAI(api_key=settings.OPENAI_API_KEY)

        system = (
            "You are a German language quiz generator. "
            "Generate multiple-choice questions with exactly one correct answer. "
            "Return only valid JSON in the specified schema."
        )
        user = {
            "instruction": "Generate German quiz questions.",
            "track": track or "mixed",
            "level": level or "A2",
            "size": max(1, int(size)),
            "schema": {
                "id": "string-unique",
                "type": "mcq",
                "question": "text",
                "options": ["A", "B", "C"],
                "answer": "one of options",
                "skills": ["articles" | "pluralization" | "cases" | "nouns" | "prepositions"],
            },
        }
        prompt = f"System:\n{system}\nUser:\n{json.dumps(user)}"

        # Use responses API if available; otherwise fallback to chat.completions
        try:
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": json.dumps(user)},
                ],
                temperature=0.7,
            )
            content = resp.choices[0].message.content or "[]"
        except Exception:
            return []

        # Extract JSON array from content
        try:
            parsed = json.loads(content)
            if isinstance(parsed, dict) and "questions" in parsed:
                items = parsed["questions"]
            elif isinstance(parsed, list):
                items = parsed
            else:
                return []
        except Exception:
            # Try to find JSON block heuristically
            start = content.find("[")
            end = content.rfind("]")
            if start != -1 and end != -1 and end > start:
                try:
                    items = json.loads(content[start : end + 1])
                except Exception:
                    return []
            else:
                return []

        # Validate and normalize
        out: List[Dict[str, Any]] = []
        for i, q in enumerate(items):
            if not isinstance(q, dict):
                continue
            if q.get("type") != "mcq":
                continue
            opts = q.get("options") or []
            ans = q.get("answer")
            if not (isinstance(opts, list) and len(opts) >= 3 and ans in opts):
                continue
            qid = str(q.get("id") or f"ai_{track or 'mixed'}_{i}")
            skills = q.get("skills") or ([track] if track else [])
            out.append({
                "id": qid,
                "type": "mcq",
                "question": q.get("question") or q.get("sentence") or "",
                "options": opts,
                "answer": ans,
                "skills": skills,
            })
            if len(out) >= size:
                break
        return out
    except Exception:
        return []
