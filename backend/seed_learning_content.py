"""Idempotently add Nebula's pilot lessons and CSV-backed practice quizzes to MongoDB.

Adds source-keyed records and extends an unchanged, source-controlled quiz only
when its stored questions are an exact prefix of the CSV bank. Admin-edited
content is left untouched. Run from backend/ after curriculum import.
"""
from __future__ import annotations

import os
import json
import hashlib

from dotenv import load_dotenv
from pymongo import MongoClient

from curated_practice import curated_practice_quizzes
from seed_pilot_lessons import seed_lessons
from starter_quizzes import starter_quizzes


# SHA-256 signatures of the five original, source-controlled pilot quizzes.
# Only an exact match is eligible for migration to the revised CSV question
# bank; edited or otherwise changed quizzes are left untouched.
LEGACY_PILOT_SIGNATURES = {
    "DSA": "05b30db5c7ff610d9eb54b8216fb25096c216a12ef9249f13cc2c50dd8fd8814",
    "PY": "721e87880c849ae4b337e69d870d4019bfe68fa5dc772ffabc502286a7e8bf22",
    "DBMS": "eb114e7596c1474c2884936e97a7a7e136ba1ebb38a21d4fabf830d03c1762df",
    "CN": "73849560f2a3515e56c6ce3edf422c9e698b7512c4cff3b640cb5efdb9b29e98",
    "OS": "f2e5d9c91fde1ad416898138d66dd5bbfae4904c34af037675b4484df30387ec",
}


def _question_content_signature(questions):
    """Compare the learner-facing question content without its review metadata."""
    fields = ("prompt", "topic", "options", "answer_index", "explanation")
    content = [{key: question.get(key) for key in fields} for question in questions]
    payload = json.dumps(content, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _can_migrate_original_pilot(existing, expected_signature):
    """Identify only the untouched, known v1 pilot document shape."""
    return bool(
        existing
        and existing.get("source") == "Nebula curated practice v1"
        and existing.get("seed_key", "").startswith("nebula-practice-v1:")
        and existing.get("difficulty") == "mixed"
        and existing.get("assessment_type") == "topic_practice"
        and existing.get("published") is True
        and _question_content_signature(existing.get("questions", [])) == expected_signature
    )


def _can_extend_unchanged_seeded_quiz(existing, quiz):
    """Allow source-bank additions only when the stored quiz is an exact prefix.

    Admin-edited content is deliberately preserved: a changed, reordered, or
    removed question makes the prefix signature differ and blocks this update.
    """
    existing_questions = existing.get("questions", []) if existing else []
    source_questions = quiz.get("questions", [])
    return bool(
        existing
        and existing.get("source") == quiz.get("source") == "Nebula-authored starter practice"
        and existing.get("seed_key") == quiz.get("seed_key")
        and existing.get("title") == quiz.get("title")
        and existing.get("assessment_type") == quiz.get("assessment_type")
        and existing.get("topic") == quiz.get("topic")
        and existing.get("difficulty") == quiz.get("difficulty")
        and existing.get("description") == (
            f"A {len(existing_questions)}-question course-wide practice set. "
            "Each question is tagged to its own outline topic and includes an explanation. "
            "This is starter practice, not a complete exam syllabus."
        )
        and existing.get("published") is True
        and 3 <= len(existing_questions) < len(source_questions)
        and _question_content_signature(existing_questions)
        == _question_content_signature(source_questions[:len(existing_questions)])
    )


def seed_learning_content(db):
    db.quizzes.create_index("seed_key", unique=True, sparse=True)
    quizzes = curated_practice_quizzes()  # Validate the complete CSV before any quiz writes.
    lessons_added, lessons_present = seed_lessons(db)
    quizzes_added = 0
    quizzes_present = 0
    quizzes_migrated = 0
    diagnostics_migrated = 0
    for quiz in quizzes:
        result = db.quizzes.update_one(
            {"seed_key": quiz["seed_key"]},
            {"$setOnInsert": quiz},
            upsert=True,
        )
        quizzes_added += int(result.upserted_id is not None)
        quizzes_present += int(result.upserted_id is None)
        if result.upserted_id is None:
            existing = db.quizzes.find_one({"seed_key": quiz["seed_key"]})
            existing_questions = existing.get("questions", []) if existing else []
            expected_legacy_signature = LEGACY_PILOT_SIGNATURES.get(quiz["course_id"])
            expected_legacy_title = f"{quiz['title']}"
            expected_legacy_topic = f"{quiz['title'].removesuffix(' focused practice')} - Fundamentals & Core Concepts"
            if (expected_legacy_signature
                    and existing
                    and existing.get("source") == "Nebula curated practice v1"
                    and existing.get("title") == expected_legacy_title
                    and existing.get("topic") == expected_legacy_topic
                    and _can_migrate_original_pilot(existing, expected_legacy_signature)):
                # Migrate only the exact built-in v1 pilot content; any edited
                # prompt/options/answer/explanation or metadata prevents this.
                db.quizzes.update_one({"_id": existing["_id"]}, {"$set": {
                    "questions": quiz["questions"],
                    "topic": quiz["topic"],
                    "description": quiz["description"],
                    "source": quiz["source"],
                    "content_review_status": quiz["content_review_status"],
                    "assessment_type": quiz["assessment_type"],
                    "seed_content_revision": 2,
                }})
                quizzes_migrated += 1
                continue
            if _can_extend_unchanged_seeded_quiz(existing, quiz):
                # Preserve any instructor review evidence on the unchanged
                # prefix; the newly appended questions stay pending.
                questions = [dict(question) for question in quiz["questions"]]
                review_fields = (
                    "review_status", "reviewer_name", "reviewer_role",
                    "source_url", "review_notes", "review_date",
                )
                for index, old_question in enumerate(existing_questions):
                    for field in review_fields:
                        if old_question.get(field):
                            questions[index][field] = old_question[field]
                db.quizzes.update_one({"_id": existing["_id"]}, {"$set": {
                    "questions": questions,
                    "topic": quiz["topic"],
                    "description": quiz["description"],
                    "content_review_status": "instructor_review_pending",
                    "seed_content_revision": 3,
                }})
                quizzes_migrated += 1
                continue
            # Carry CSV review evidence forward only while the question wording,
            # options, answer key and explanation still exactly match the bank.
            # This leaves admin-edited quizzes fully intact.
            if len(existing_questions) == len(quiz["questions"]) and _question_content_signature(existing_questions) == _question_content_signature(quiz["questions"]):
                review_update = {
                    "content_review_status": quiz["content_review_status"],
                }
                if "reviewed_at" in quiz:
                    review_update["reviewed_at"] = quiz["reviewed_at"]
                for index, question in enumerate(quiz["questions"]):
                    for field in ("review_status", "reviewer_name", "reviewer_role", "source_url", "review_notes", "review_date"):
                        review_update[f"questions.{index}.{field}"] = question.get(field, "")
                update = {"$set": review_update}
                if "reviewed_at" not in quiz:
                    update["$unset"] = {"reviewed_at": ""}
                db.quizzes.update_one({"_id": existing["_id"]}, update)

    # Extend only exact, source-controlled Nebula baseline quizzes. The prefix
    # signature check prevents this seeding command from replacing admin edits.
    for diagnostic in starter_quizzes():
        existing = db.quizzes.find_one({
            "course_id": diagnostic["course_id"],
            "title": diagnostic["title"],
            "source": "nebula_starter",
        })
        old_questions = existing.get("questions", []) if existing else []
        new_questions = diagnostic.get("questions", [])
        if not (existing and existing.get("published") is True
                and 1 <= len(old_questions) < 15
                and len(new_questions) == 15
                and _question_content_signature(old_questions)
                == _question_content_signature(new_questions[:len(old_questions)])):
            continue
        questions = [dict(question) for question in new_questions]
        review_fields = ("review_status", "reviewer_name", "reviewer_role", "source_url", "review_notes", "review_date")
        for index, old_question in enumerate(old_questions):
            for field in review_fields:
                if old_question.get(field):
                    questions[index][field] = old_question[field]
        db.quizzes.update_one({"_id": existing["_id"], "source": "nebula_starter"}, {"$set": {
            "questions": questions,
            "content_review_status": "instructor_review_pending",
            "seed_content_revision": 2,
        }})
        diagnostics_migrated += 1
    return lessons_added, lessons_present, quizzes_added, quizzes_present, quizzes_migrated, diagnostics_migrated


def main():
    load_dotenv()
    uri = os.getenv("MONGODB_URI")
    if not uri:
        raise SystemExit("MONGODB_URI is missing; no changes were made.")
    client = MongoClient(uri, serverSelectionTimeoutMS=10000)
    try:
        client.admin.command("ping")
        database = os.getenv("MONGODB_DB", "nebula")
        added_lessons, existing_lessons, added_quizzes, existing_quizzes, migrated_quizzes, migrated_diagnostics = seed_learning_content(client[database])
        print(
            "Pilot content ready: "
            f"{added_lessons} lessons added, {existing_lessons} lessons already present; "
            f"{added_quizzes} CSV-backed focused practice quizzes added, "
            f"{migrated_quizzes} unchanged CSV-backed practice quizzes refreshed, "
            f"{migrated_diagnostics} unchanged baseline diagnostics extended to 15, "
            f"{existing_quizzes - migrated_quizzes} existing practice quizzes preserved."
        )
    finally:
        client.close()


if __name__ == "__main__":
    main()
