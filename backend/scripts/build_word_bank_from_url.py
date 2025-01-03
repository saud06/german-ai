#!/usr/bin/env python
"""
Build a curated word bank JSON (500+ entries) locally from a public URL
and save it to backend/seed/word_bank_large.json, ready for the
/dev/seed-from-file admin endpoint.

Usage:
  python backend/scripts/build_word_bank_from_url.py \
    --url https://example.com/german_words.csv \
    --count 500

The URL can be:
- JSON array of objects with keys: level, word, translation, example
- or CSV with header: level,word,translation,example

Notes:
- This script runs locally and writes backend/seed/word_bank_large.json
- It does not touch the database. After building, call the admin endpoint:
    POST /api/v1/admin/dev/seed-from-file?filename=word_bank_large.json&count=500

"""

import argparse
import csv
import io
import json
import os
from pathlib import Path
from typing import List, Dict
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
SEED_DIR = ROOT / "seed"
OUT_FILE = SEED_DIR / "word_bank_large.json"


def fetch(url: str) -> bytes:
    with urllib.request.urlopen(url) as resp:
        return resp.read()


def normalize_entries(raw_text: str) -> List[Dict]:
    # Try JSON first
    try:
        data = json.loads(raw_text)
        if isinstance(data, list):
            return [x for x in data if isinstance(x, dict)]
    except Exception:
        pass
    # Try CSV
    try:
        rd = csv.DictReader(io.StringIO(raw_text))
        return list(rd)
    except Exception:
        pass
    raise ValueError("Unsupported content; expected JSON array or CSV with header")


def to_docs(entries: List[Dict], count: int) -> List[Dict]:
    seen = set()
    docs: List[Dict] = []
    for it in entries:
        if not isinstance(it, dict):
            continue
        word = (it.get("word") or it.get("term") or "").strip()
        if not word or word in seen:
            continue
        seen.add(word)
        level = (it.get("level") or "A1").strip()
        translation = (it.get("translation") or it.get("en") or "").strip()
        example = (it.get("example") or it.get("sentence") or "").strip()
        docs.append({
            "level": level,
            "word": word,
            "translation": translation,
            "example": example,
        })
        if len(docs) >= count:
            break
    if not docs:
        raise ValueError("No valid entries after normalization")
    return docs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True)
    ap.add_argument("--count", type=int, default=500)
    args = ap.parse_args()

    raw = fetch(args.url)
    entries = normalize_entries(raw.decode("utf-8"))
    docs = to_docs(entries, args.count)

    os.makedirs(SEED_DIR, exist_ok=True)
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(docs, f, ensure_ascii=False, indent=2)
    print(f"Wrote {len(docs)} entries to {OUT_FILE}")


if __name__ == "__main__":
    main()
