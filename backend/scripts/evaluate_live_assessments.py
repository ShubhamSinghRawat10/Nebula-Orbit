"""Evaluate a candidate model on pseudonymized live quiz attempts from MongoDB.

Reads attempts from the configured database, maps exact course/topic names to
the local catalog, hashes learner/attempt IDs in memory, and writes only the
candidate model and aggregate metrics. Raw attempts are never exported.
"""
from __future__ import annotations

import csv
import hashlib
import hmac
import json
import os
import sys
import tempfile
from collections import Counter
from datetime import date, datetime
from pathlib import Path

from dotenv import load_dotenv
import joblib
from pymongo import MongoClient

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.train_performance_model import main as train_model

DATA_DIR = ROOT / "data"
MODEL_DIR = ROOT / "models"
OUTPUT_MODEL = MODEL_DIR / "performance_model_live_candidate.joblib"
OUTPUT_METRICS = MODEL_DIR / "performance_model_live_metrics.json"
FIELDS = [
    "interaction_id", "student_id", "student_name", "course_code", "topic_id",
    "topic_name", "test_score", "proficiency_status", "recommendation", "last_assessed",
    "assessment_id", "last_assessed_at",
]


def pseudonym(secret: bytes, value: object) -> str:
    return hmac.new(secret, str(value).encode("utf-8"), hashlib.sha256).hexdigest()


def proficiency(score: float) -> str:
    return "Weak" if score < 50 else "Intermediate" if score < 80 else "Mastered"


def main() -> int:
    load_dotenv(ROOT / ".env")
    uri = os.getenv("MONGODB_URI", "").strip()
    database_name = os.getenv("MONGODB_DB", "").strip()
    salt = os.getenv("DATASET_HASH_SALT", "").encode("utf-8")
    if not uri or not database_name:
        print("Missing MONGODB_URI or MONGODB_DB in backend/.env.", file=sys.stderr)
        return 2
    if len(salt) < 24:
        print("Set DATASET_HASH_SALT to a private secret of at least 24 characters in backend/.env.", file=sys.stderr)
        return 2

    topic_catalog = {}
    with (DATA_DIR / "topics.csv").open("r", encoding="utf-8-sig", newline="") as stream:
        for topic in csv.DictReader(stream):
            topic_catalog[(topic["course_code"].strip().upper(), topic["topic_name"].strip())] = topic["topic_id"].strip()

    client = None
    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=8000, connectTimeoutMS=8000)
        client.admin.command("ping")
        attempts = client[database_name]["attempts"]
        cursor = attempts.find(
            {},
            {"_id": 1, "student_id": 1, "course_id": 1, "topic": 1,
             "topic_scores": 1, "score": 1, "max_score": 1, "created_at": 1},
        )
        docs = list(cursor)
    except Exception as exc:
        # Do not print the Mongo URI or exception text, which may contain host details.
        print(f"Could not read live attempts from MongoDB ({type(exc).__name__}). Check the local Atlas connection and IP access list.", file=sys.stderr)
        return 3
    finally:
        if client is not None:
            client.close()

    rows = []
    catalog_topic_rows = 0
    evaluation_only_topic_rows = 0
    unmapped_topics = Counter()
    distinct_students = set()
    for attempt in docs:
        course_code = str(attempt.get("course_id") or "").strip().upper()
        student_key = attempt.get("student_id")
        attempt_key = attempt.get("_id")
        assessed = attempt.get("created_at")
        if not course_code or student_key is None or attempt_key is None or assessed is None:
            continue
        if isinstance(assessed, datetime):
            assessed_day = assessed.date().isoformat()
            assessed_at = assessed.isoformat()
        elif isinstance(assessed, date):
            assessed_day = assessed.isoformat()
            assessed_at = ""
        else:
            try:
                parsed_assessed = datetime.fromisoformat(str(assessed).replace("Z", "+00:00"))
                assessed_day = parsed_assessed.date().isoformat()
                assessed_at = parsed_assessed.isoformat()
            except ValueError:
                continue

        breakdown = attempt.get("topic_scores") or [{
            "topic": attempt.get("topic", ""),
            "score": attempt.get("score", 0),
            "max_score": attempt.get("max_score", 0),
        }]
        for result in breakdown:
            topic_name = str(result.get("topic") or "").strip()
            topic_id = topic_catalog.get((course_code, topic_name))
            if not topic_id:
                unmapped_topics[(course_code, topic_name)] += 1
                evaluation_only_topic_rows += 1
                # Preserve stable live quiz labels for diagnostics without
                # pretending they are IDs in the production topic catalog.
                topic_id = "LIVE_" + hashlib.sha256(f"{course_code}\0{topic_name}".encode("utf-8")).hexdigest()[:24]
            else:
                catalog_topic_rows += 1
            try:
                raw_score = float(result.get("score", 0))
                maximum = float(result.get("max_score", 0))
            except (TypeError, ValueError):
                continue
            if maximum <= 0:
                continue
            score = round(max(0.0, min(100.0, 100.0 * raw_score / maximum)), 3)
            student_hash = pseudonym(salt, student_key)
            interaction_hash = pseudonym(salt, f"{attempt_key}:{topic_id}")
            distinct_students.add(student_hash)
            rows.append({
                "interaction_id": f"LIVE_INT_{interaction_hash[:32]}",
                "student_id": f"LIVE_STU_{student_hash[:32]}",
                "student_name": "",
                "course_code": course_code,
                "topic_id": topic_id,
                "topic_name": topic_name,
                "test_score": score,
                "proficiency_status": proficiency(score),
                "recommendation": "",
                "last_assessed": assessed_day,
                # Multiple topic scores from one quiz share an event key. This
                # lets evaluation use earlier quizzes from the same day without
                # leaking scores between topics in the same quiz.
                "assessment_id": f"LIVE_ATT_{pseudonym(salt, attempt_key)[:32]}",
                "last_assessed_at": assessed_at,
            })

    dates = {row["last_assessed"] for row in rows}
    if len(rows) < 30 or len(dates) < 4 or len(distinct_students) < 2:
        print(
            f"Not enough live assessment history: {len(rows)} rows across {len(dates)} dates from {len(distinct_students)} learners; "
            f"{catalog_topic_rows} rows matched topics.csv and {evaluation_only_topic_rows} use evaluation-only topic IDs. "
            "Need at least 4 assessment dates and 2 learners for a chronological evaluation.",
            file=sys.stderr,
        )
        if unmapped_topics:
            print("Most common unmatched course/topic labels:", file=sys.stderr)
            for (course_code, topic_name), count in unmapped_topics.most_common(8):
                print(f"  {course_code} | {topic_name[:100]} ({count})", file=sys.stderr)
        return 4

    with tempfile.TemporaryDirectory(prefix="nebula_live_eval_") as temp_dir:
        dataset_path = Path(temp_dir) / "pseudonymized_live_assessments.csv"
        with dataset_path.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=FIELDS)
            writer.writeheader()
            writer.writerows(rows)
        print(f"Evaluating {len(rows)} mapped assessment rows from {len(distinct_students)} pseudonymized learners across {len(dates)} dates.")
        print(f"{catalog_topic_rows} rows use official topic IDs; {evaluation_only_topic_rows} use evaluation-only IDs.")
        metrics = train_model(dataset_path, OUTPUT_MODEL, OUTPUT_METRICS)
        metrics["catalog_topic_rows"] = catalog_topic_rows
        metrics["evaluation_only_topic_rows"] = evaluation_only_topic_rows
        metrics["candidate_app_compatible"] = evaluation_only_topic_rows == 0
        if evaluation_only_topic_rows:
            metrics["student_facing_eligible"] = False
        OUTPUT_METRICS.write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")
        artifact = joblib.load(OUTPUT_MODEL)
        artifact["metrics"] = metrics
        joblib.dump(artifact, OUTPUT_MODEL, compress=3)
        if evaluation_only_topic_rows:
            print("Candidate uses live quiz topic labels absent from topics.csv; do not use it for app predictions until those topics are formally mapped.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
