"""Load Nebula's curriculum and safely pseudonymized assessment history."""
from __future__ import annotations

import csv
import hashlib
import hmac
import os
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from pymongo import ASCENDING, UpdateOne


def read_csv(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def _bulk_upsert(collection, docs, key, batch_size=750):
    # mongomock's BulkOperationBuilder lags current PyMongo's UpdateOne shape;
    # use regular upserts for the small demo curriculum in that environment.
    if collection.__class__.__module__.startswith("mongomock"):
        for doc in docs:
            collection.update_one({key: doc[key]}, {"$set": doc}, upsert=True)
        return len(docs)
    count = 0
    for start in range(0, len(docs), batch_size):
        batch = docs[start:start + batch_size]
        operations = [UpdateOne({key: doc[key]}, {"$set": doc}, upsert=True) for doc in batch]
        if operations:
            collection.bulk_write(operations, ordered=False)
            count += len(operations)
    return count


def import_curriculum(db, data_dir: str | Path):
    root = Path(data_dir)
    course_rows = read_csv(root / "courses.csv")
    topic_rows = read_csv(root / "topics.csv")
    prerequisite_rows = read_csv(root / "topic_prerequisite.csv")
    if not course_rows or not topic_rows:
        raise ValueError("courses.csv and topics.csv must each contain at least one row.")
    grouped_topics = defaultdict(list)
    for row in topic_rows:
        grouped_topics[row["course_code"].upper()].append(row)

    course_docs = []
    for row in course_rows:
        code = row["course_code"].upper()
        topics = grouped_topics[code]
        names = [topic["topic_name"] for topic in topics]
        category = row["category"]
        description = f"A {category.lower()} course covering {', '.join(names[:3])}" + (f" and {len(names) - 3} more topics." if len(names) > 3 else ".")
        course_docs.append({
            "course_id": code,
            "title": row["course_name"],
            "subject": category,
            "category": category,
            "level": "All levels",
            "description": description,
            "estimated_hours": sum(int(topic["estimated_hours"]) for topic in topics),
            "topics": names,
            "topic_ids": [topic["topic_id"] for topic in topics],
            "created_at": datetime.now(timezone.utc),
            "source": "nebula_curriculum_csv",
        })

    topic_docs = [{
        "topic_id": row["topic_id"],
        "course_id": row["course_code"].upper(),
        "topic_name": row["topic_name"],
        "difficulty_level": row["difficulty_level"],
        "estimated_hours": int(row["estimated_hours"]),
        "source": "nebula_curriculum_csv",
    } for row in topic_rows]
    prerequisite_docs = [{
        "edge_id": row["id"],
        "topic_id": row["topic_id"],
        "prerequisite_topic_id": row["prerequisite_topic_id"],
        "prerequisite_type": row["prerequisite_type"],
        "source": "nebula_curriculum_csv",
    } for row in prerequisite_rows]

    db.courses.create_index([("course_id", ASCENDING)], unique=True)
    db.topics.create_index([("topic_id", ASCENDING)], unique=True)
    db.prerequisites.create_index([("edge_id", ASCENDING)], unique=True)
    # Keep CSV-owned catalog rows in sync while preserving admin-created records.
    db.courses.delete_many({"source": "nebula_curriculum_csv", "course_id": {"$nin": [doc["course_id"] for doc in course_docs]}})
    db.topics.delete_many({"source": "nebula_curriculum_csv", "topic_id": {"$nin": [doc["topic_id"] for doc in topic_docs]}})
    db.prerequisites.delete_many({"edge_id": {"$exists": True, "$nin": [doc["edge_id"] for doc in prerequisite_docs]}})
    counts = {
        "courses": _bulk_upsert(db.courses, course_docs, "course_id"),
        "topics": _bulk_upsert(db.topics, topic_docs, "topic_id"),
        "prerequisites": _bulk_upsert(db.prerequisites, prerequisite_docs, "edge_id"),
    }
    db.dataset_metadata.update_one(
        {"_id": "curriculum"},
        {"$set": {"counts": counts, "source_files": ["courses.csv", "topics.csv", "topic_prerequisite.csv"], "updated_at": datetime.now(timezone.utc)}},
        upsert=True,
    )
    return counts


def import_interaction_history(db, data_dir: str | Path, salt: str):
    """Import performance rows without storing names or raw student IDs.

    `student_name` is deliberately discarded. Student and row identifiers are
    HMAC-pseudonymized with a locally configured secret so history can only be
    joined across records by this project and cannot be matched to app accounts.
    """
    if len(salt) < 24:
        raise ValueError("DATASET_HASH_SALT must contain at least 24 characters.")
    rows = read_csv(Path(data_dir) / "student_interaction.csv")
    key = salt.encode("utf-8")
    docs = []
    for row in rows:
        student_key = hmac.new(key, ("student:" + row["student_id"]).encode(), hashlib.sha256).hexdigest()
        record_key = hmac.new(key, ("interaction:" + row["interaction_id"]).encode(), hashlib.sha256).hexdigest()
        assessed = datetime.strptime(row["last_assessed"], "%Y-%m-%d").replace(tzinfo=timezone.utc)
        docs.append({
            "record_key": record_key,
            "student_key": student_key,
            "course_id": row["course_code"].upper(),
            "topic_id": row["topic_id"],
            "topic_name": row["topic_name"],
            "test_score": float(row["test_score"]),
            "proficiency_status": row["proficiency_status"],
            "recommendation_label": row["recommendation"],
            "last_assessed": assessed,
            "source": "nebula_student_interaction_csv",
        })

    db.dataset_interactions.create_index([("record_key", ASCENDING)], unique=True)
    db.dataset_interactions.create_index([("student_key", ASCENDING), ("topic_id", ASCENDING), ("last_assessed", ASCENDING)])
    db.dataset_interactions.delete_many({"source": "nebula_student_interaction_csv", "record_key": {"$nin": [doc["record_key"] for doc in docs]}})
    count = _bulk_upsert(db.dataset_interactions, docs, "record_key")
    db.dataset_metadata.update_one(
        {"_id": "student_interactions"},
        {"$set": {"count": count, "source_file": "student_interaction.csv", "contains_names": False, "student_ids_pseudonymized": True, "updated_at": datetime.now(timezone.utc)}},
        upsert=True,
    )
    return count
