#!/usr/bin/env python
"""
Import real-life seed words into the database from a CSV file.

Usage:
  python scripts/import_seed_words.py backend/seed/seed_words.csv

CSV columns (header required): level,word,translation,example
- level: A1|A2|B1|B2|C1|C2
- word: e.g., "die Herausforderung"
- translation: e.g., "the challenge"
- example: e.g., "Das ist eine große Herausforderung."

Notes:
- Reads Mongo settings from backend/.env (MONGODB_URI, MONGODB_DB_NAME)
- Upserts by exact word string to avoid duplicates.
"""
import csv
import os
import sys
from pathlib import Path
from typing import Iterable

from dotenv import load_dotenv
from pymongo import MongoClient, UpdateOne

ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = ROOT / ".env"


def batched(iterable: Iterable, n: int):
    batch = []
    for item in iterable:
        batch.append(item)
        if len(batch) >= n:
            yield batch
            batch = []
    if batch:
        yield batch


def main():
    if len(sys.argv) < 2:
        print("Provide path to CSV. Example: python scripts/import_seed_words.py backend/seed/seed_words.csv")
        sys.exit(1)

    csv_path = Path(sys.argv[1]).resolve()
    if not csv_path.exists():
        print(f"CSV not found: {csv_path}")
        sys.exit(1)

    load_dotenv(dotenv_path=ENV_PATH)
    uri = os.getenv("MONGODB_URI")
    db_name = os.getenv("MONGODB_DB_NAME")
    if not uri:
        print("MONGODB_URI not set in backend/.env")
        sys.exit(1)

    client = MongoClient(uri)
    db = client[db_name] if db_name else client.get_default_database()
    coll = db["seed_words"]

    to_write = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        required = {"level", "word", "translation", "example"}
        if set(reader.fieldnames or []) < required:
            print(f"CSV must have columns: {', '.join(sorted(required))}")
            sys.exit(1)
        for row in reader:
            word = (row.get("word") or "").strip()
            if not word:
                continue
            doc = {
                "level": (row.get("level") or "A1").strip(),
                "word": word,
                "translation": (row.get("translation") or "").strip(),
                "examples": [ (row.get("example") or "").strip() ],
            }
            to_write.append(UpdateOne({"word": word}, {"$set": doc}, upsert=True))

    total = 0
    for chunk in batched(to_write, 500):
        res = coll.bulk_write(chunk, ordered=False)
        total += res.upserted_count + res.modified_count

    print(f"Imported/updated {total} words from {csv_path}")


if __name__ == "__main__":
    main()
