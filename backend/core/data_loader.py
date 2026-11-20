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
    track_path = root / "course_tracks.csv"
    course_track_rows = read_csv(track_path) if track_path.exists() else []
    branch_path = root / "branch_curriculum.csv"
    branch_rows = read_csv(branch_path) if branch_path.exists() else []
    tracks_path = root / "curriculum_tracks.csv"
    track_rows = read_csv(tracks_path) if tracks_path.exists() else []
    parents_path = root / "curriculum_track_parents.csv"
    parent_rows = read_csv(parents_path) if parents_path.exists() else []
    if not course_rows or not topic_rows:
        raise ValueError("courses.csv and topics.csv must each contain at least one row.")
    grouped_topics = defaultdict(list)
    known_topic_ids = set()
    for row in topic_rows:
        topic_id = str(row.get("topic_id", "")).strip()
        course_code = str(row.get("course_code", "")).strip().upper()
        if not topic_id or not course_code:
            raise ValueError("Every topic row needs a topic_id and course_code.")
        if topic_id in known_topic_ids:
            raise ValueError(f"Duplicate topic_id in topics.csv: {topic_id}.")
        known_topic_ids.add(topic_id)
        grouped_topics[course_code].append(row)

    grouped_tracks = defaultdict(list)
    known_tracks = {str(row.get("track_id", "")).strip().upper() for row in track_rows if row.get("track_id")}
    if len(known_tracks) != len(track_rows):
        raise ValueError("curriculum_tracks.csv has a blank or duplicate track_id.")
    known_course_codes = {str(row.get("course_code", "")).strip().upper() for row in course_rows if row.get("course_code")}
    for row in course_track_rows:
        code = str(row.get("course_code", "")).strip().upper()
        track_id = str(row.get("track_id", "")).strip().upper()
        if not code or not track_id:
            raise ValueError("Every course_tracks.csv row needs a course_code and track_id.")
        if known_tracks and track_id not in known_tracks:
            raise ValueError(f"Unknown program track {track_id} in course_tracks.csv.")
        if code not in known_course_codes:
            raise ValueError(f"Unknown course {code} in course_tracks.csv.")
        if code and track_id and track_id not in grouped_tracks[code]:
            grouped_tracks[code].append(track_id)
    parent_edges = set()
    for row in parent_rows:
        child = str(row.get("track_id", "")).strip().upper()
        parent = str(row.get("parent_track_id", "")).strip().upper()
        if not child or not parent or child == parent or (child, parent) in parent_edges:
            raise ValueError("curriculum_track_parents.csv has a blank, self-referencing, or duplicate mapping.")
        parent_edges.add((child, parent))
        if known_tracks and (child not in known_tracks or parent not in known_tracks):
            raise ValueError(f"Unknown curriculum track in inheritance mapping: {child} <- {parent}.")
        for code, mapped_tracks in list(grouped_tracks.items()):
            if parent in mapped_tracks and child not in mapped_tracks:
                mapped_tracks.append(child)

    branch_courses = {}
    for row in branch_rows:
        code = str(row.get("course_code", "")).strip().upper()
        track_id = str(row.get("track_id", "")).strip().upper()
        title = str(row.get("course_name", "")).strip()
        topic_names = [name.strip() for name in str(row.get("topics", "")).split("|") if name.strip()]
        if not code or not track_id or not title or not topic_names:
            raise ValueError("Every branch curriculum row needs a course code, track, title, and topics.")
        if known_tracks and track_id not in known_tracks:
            raise ValueError(f"Unknown program track {track_id} in the branch curriculum.")
        existing = branch_courses.setdefault(code, {"course_code": code, "course_name": title, "category": row.get("category", "Core"), "topics": topic_names, "program_tracks": []})
        if existing["course_name"] != title or existing["topics"] != topic_names:
            raise ValueError(f"Curriculum course {code} has conflicting definitions across tracks.")
        if track_id not in existing["program_tracks"]:
            existing["program_tracks"].append(track_id)

    for code, item in branch_courses.items():
        if code not in grouped_topics:
            grouped_topics[code] = [{
                "topic_id": f"{code}_T{index}", "course_code": code,
                "topic_name": name, "difficulty_level": "Beginner" if index <= 2 else "Intermediate",
                "estimated_hours": 3,
            } for index, name in enumerate(item["topics"], 1)]
        grouped_tracks[code] = list(dict.fromkeys(grouped_tracks.get(code, []) + item["program_tracks"]))
    unmapped_courses = sorted(row["course_code"].upper() for row in course_rows if not grouped_tracks.get(row["course_code"].upper()))
    if unmapped_courses:
        raise ValueError("Every existing course must be assigned to at least one program track: " + ", ".join(unmapped_courses))

    all_course_rows = list(course_rows)
    known_codes = {row["course_code"].upper() for row in course_rows}
    all_course_rows.extend({"course_code": code, "course_name": item["course_name"], "category": item["category"]}
                           for code, item in branch_courses.items() if code not in known_codes)
    course_docs = []
    for row in all_course_rows:
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
            "program_tracks": grouped_tracks.get(code, []),
            "created_at": datetime.now(timezone.utc),
            "source": "nebula_curriculum_csv",
        })

    all_topic_rows = list(topic_rows)
    all_topic_rows.extend(topic for code in branch_courses for topic in grouped_topics[code]
                          if topic["topic_id"] not in known_topic_ids)
    topic_docs = [{
        "topic_id": row["topic_id"],
        "course_id": row["course_code"].upper(),
        "topic_name": row["topic_name"],
        "difficulty_level": row["difficulty_level"],
        "estimated_hours": int(row["estimated_hours"]),
        "source": "nebula_curriculum_csv",
    } for row in all_topic_rows]
    prerequisite_docs = [{
        "edge_id": row["id"],
        "topic_id": row["topic_id"],
        "prerequisite_topic_id": row["prerequisite_topic_id"],
        "prerequisite_type": row["prerequisite_type"],
        "source": "nebula_curriculum_csv",
    } for row in prerequisite_rows]
    track_docs = [{
        "track_id": row["track_id"].strip().upper(),
        "degree": row["degree"].strip(),
        "branch": row["branch"].strip(),
        "display_name": row["display_name"].strip(),
        "source_scope": row["source_scope"].strip(),
        "source": "nebula_curriculum_csv",
    } for row in track_rows]

    db.courses.create_index([("course_id", ASCENDING)], unique=True)
    db.topics.create_index([("topic_id", ASCENDING)], unique=True)
    db.prerequisites.create_index([("edge_id", ASCENDING)], unique=True)
    db.curriculum_tracks.create_index([("track_id", ASCENDING)], unique=True)
    # Keep CSV-owned catalog rows in sync while preserving admin-created records.
    db.courses.delete_many({"source": "nebula_curriculum_csv", "course_id": {"$nin": [doc["course_id"] for doc in course_docs]}})
    db.topics.delete_many({"source": "nebula_curriculum_csv", "topic_id": {"$nin": [doc["topic_id"] for doc in topic_docs]}})
    # Curriculum refreshes must never delete relationships created by an admin.
    db.prerequisites.delete_many({
        "source": "nebula_curriculum_csv",
        "edge_id": {"$nin": [doc["edge_id"] for doc in prerequisite_docs]},
    })
    db.curriculum_tracks.delete_many({
        "source": "nebula_curriculum_csv",
        "track_id": {"$nin": [doc["track_id"] for doc in track_docs]},
    })
    counts = {
        "courses": _bulk_upsert(db.courses, course_docs, "course_id"),
        "topics": _bulk_upsert(db.topics, topic_docs, "topic_id"),
        "prerequisites": _bulk_upsert(db.prerequisites, prerequisite_docs, "edge_id"),
        "tracks": _bulk_upsert(db.curriculum_tracks, track_docs, "track_id"),
    }
    db.dataset_metadata.update_one(
        {"_id": "curriculum"},
        {"$set": {"counts": counts, "source_files": [f"data/{name}" for name in ("courses.csv", "topics.csv", "topic_prerequisite.csv", "course_tracks.csv", "branch_curriculum.csv", "curriculum_tracks.csv", "curriculum_track_parents.csv")], "updated_at": datetime.now(timezone.utc)}},
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
