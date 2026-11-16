"""Idempotently add Nebula's pilot lessons and focused practice quizzes to MongoDB.

Only inserts records carrying Nebula's private seed keys; existing admin-created
or edited content is left untouched. Run from backend/ after curriculum import.
"""
from __future__ import annotations

import os

from dotenv import load_dotenv
from pymongo import MongoClient

from curated_practice import curated_practice_quizzes
from seed_pilot_lessons import seed_lessons


def seed_learning_content(db):
    db.quizzes.create_index("seed_key", unique=True, sparse=True)
    lessons_added, lessons_present = seed_lessons(db)
    quizzes_added = 0
    quizzes_present = 0
    for quiz in curated_practice_quizzes():
        result = db.quizzes.update_one(
            {"seed_key": quiz["seed_key"]},
            {"$setOnInsert": quiz},
            upsert=True,
        )
        quizzes_added += int(result.upserted_id is not None)
        quizzes_present += int(result.upserted_id is None)
    return lessons_added, lessons_present, quizzes_added, quizzes_present


def main():
    load_dotenv()
    uri = os.getenv("MONGODB_URI")
    if not uri:
        raise SystemExit("MONGODB_URI is missing; no changes were made.")
    client = MongoClient(uri, serverSelectionTimeoutMS=10000)
    try:
        client.admin.command("ping")
        database = os.getenv("MONGODB_DB", "nebula")
        added_lessons, existing_lessons, added_quizzes, existing_quizzes = seed_learning_content(client[database])
        print(
            "Pilot content ready: "
            f"{added_lessons} lessons added, {existing_lessons} lessons already present; "
            f"{added_quizzes} focused practice quizzes added, {existing_quizzes} already present."
        )
    finally:
        client.close()


if __name__ == "__main__":
    main()
