"""Copy quiz documents from Nebula's local demo snapshot into MongoDB.

Only quizzes are migrated. Demo accounts, attempts, and study plans are not
copied. Existing MongoDB quiz documents are left untouched on repeat runs.
"""
from __future__ import annotations

import os
from pathlib import Path

from bson import json_util
from dotenv import load_dotenv
from pymongo import MongoClient


load_dotenv()

ROOT = Path(__file__).resolve().parent
snapshot_path = Path(
    os.getenv("NEBULA_DEMO_STORE", str(ROOT / ".demo_data.json"))
)
if not snapshot_path.is_file():
    raise SystemExit(f"Demo snapshot not found: {snapshot_path}")

snapshot = json_util.loads(snapshot_path.read_text(encoding="utf-8"))
quizzes = snapshot.get("quizzes", [])
if not isinstance(quizzes, list):
    raise SystemExit("The demo snapshot's quizzes entry is not a list.")
if any(not quiz.get("_id") or not quiz.get("course_id") or not quiz.get("questions") for quiz in quizzes):
    raise SystemExit("A quiz is missing its ID, course, or questions; nothing was imported.")

client = MongoClient(
    os.getenv("MONGODB_URI", "mongodb://127.0.0.1:27017/"),
    serverSelectionTimeoutMS=5000,
)
client.admin.command("ping")
collection = client[os.getenv("MONGODB_DB", "nebula")].quizzes

inserted = 0
already_present = 0
for quiz in quizzes:
    result = collection.update_one(
        {"_id": quiz["_id"]},
        {"$setOnInsert": quiz},
        upsert=True,
    )
    if result.upserted_id is not None:
        inserted += 1
    else:
        already_present += 1

print(
    f"Quiz migration complete: {inserted} inserted, "
    f"{already_present} already present, {len(quizzes)} total."
)
print("Only quiz documents were copied; accounts, attempts, and study plans were not copied.")
client.close()
