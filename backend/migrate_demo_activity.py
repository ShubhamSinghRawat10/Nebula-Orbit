"""Idempotently copy local student accounts, attempts, and plans to MongoDB.

Existing MongoDB accounts and plans are never overwritten. When an email is
already present, the local account is mapped to that existing account so its
attempts and plan stay attached to the current MongoDB identity.
"""
from __future__ import annotations

import os
from pathlib import Path

from bson import json_util
from dotenv import load_dotenv
from pymongo import MongoClient


load_dotenv()

ROOT = Path(__file__).resolve().parent
snapshot_path = Path(os.getenv("NEBULA_DEMO_STORE", str(ROOT / ".demo_data.json")))
if not snapshot_path.is_file():
    raise SystemExit(f"Demo snapshot not found: {snapshot_path}")

snapshot = json_util.loads(snapshot_path.read_text(encoding="utf-8"))
users_to_copy = snapshot.get("users", [])
attempts_to_copy = snapshot.get("attempts", [])
plans_to_copy = snapshot.get("study_plans", [])
if not all(isinstance(rows, list) for rows in (users_to_copy, attempts_to_copy, plans_to_copy)):
    raise SystemExit("Snapshot users, attempts, and study_plans must be lists.")

email_by_id = {}
for user in users_to_copy:
    user_id = user.get("_id")
    email = str(user.get("email", "")).strip().lower()
    if not user_id or not email:
        raise SystemExit("A snapshot account is missing its ID or email; nothing was migrated.")
    if email in email_by_id.values():
        raise SystemExit("Duplicate account emails exist in the snapshot; nothing was migrated.")
    email_by_id[user_id] = email
if any(attempt.get("student_id") not in email_by_id for attempt in attempts_to_copy):
    raise SystemExit("A snapshot attempt has no matching student account; nothing was migrated.")
if any(plan.get("student_id") not in email_by_id for plan in plans_to_copy):
    raise SystemExit("A snapshot plan has no matching student account; nothing was migrated.")

client = MongoClient(
    os.getenv("MONGODB_URI", "mongodb://127.0.0.1:27017/"),
    serverSelectionTimeoutMS=8000,
)
try:
    client.admin.command("ping")
    db = client[os.getenv("MONGODB_DB", "nebula")]
    users = db.users
    attempts = db.attempts
    plans = db.study_plans

    # Preflight quiz references before making any writes, so saved attempts do
    # not point at quiz documents that were not migrated.
    quiz_ids = {attempt.get("quiz_id") for attempt in attempts_to_copy if attempt.get("quiz_id")}
    missing_quiz_ids = [quiz_id for quiz_id in quiz_ids if not db.quizzes.find_one({"_id": quiz_id}, {"_id": 1})]
    if missing_quiz_ids:
        raise SystemExit(f"{len(missing_quiz_ids)} referenced quiz documents are missing; migrate quizzes first.")

    existing_users = {
        str(row.get("email", "")).strip().lower(): row["_id"]
        for row in users.find({}, {"email": 1})
        if row.get("email")
    }
    mapped_user_ids = {}
    accounts_inserted = 0
    accounts_matched = 0
    for source_user in users_to_copy:
        source_id = source_user["_id"]
        email = email_by_id[source_id]
        by_id = users.find_one({"_id": source_id}, {"_id": 1})
        if by_id:
            mapped_user_ids[source_id] = by_id["_id"]
            accounts_matched += 1
        elif email in existing_users:
            mapped_user_ids[source_id] = existing_users[email]
            accounts_matched += 1
        else:
            normalized_user = dict(source_user)
            normalized_user["email"] = email
            users.insert_one(normalized_user)
            mapped_user_ids[source_id] = source_id
            existing_users[email] = source_id
            accounts_inserted += 1

    attempts_inserted = 0
    attempts_present = 0
    for source_attempt in attempts_to_copy:
        attempt = dict(source_attempt)
        attempt["student_id"] = mapped_user_ids[attempt["student_id"]]
        if attempt.get("_id") and attempts.find_one({"_id": attempt["_id"]}, {"_id": 1}):
            attempts_present += 1
            continue
        attempts.insert_one(attempt)
        attempts_inserted += 1

    plans_inserted = 0
    plans_present = 0
    for source_plan in plans_to_copy:
        plan = dict(source_plan)
        plan["student_id"] = mapped_user_ids[plan["student_id"]]
        if plans.find_one({"student_id": plan["student_id"]}, {"_id": 1}):
            plans_present += 1
            continue
        # Plan IDs are not referenced elsewhere; let MongoDB assign a fresh ID
        # to avoid collisions with an unrelated existing plan.
        plan.pop("_id", None)
        plans.insert_one(plan)
        plans_inserted += 1

    print({
        "accounts_inserted": accounts_inserted,
        "accounts_already_present_or_matched": accounts_matched,
        "attempts_inserted": attempts_inserted,
        "attempts_already_present": attempts_present,
        "plans_inserted": plans_inserted,
        "plans_already_present": plans_present,
    })
    print("Existing MongoDB account credentials and study plans were not overwritten.")
finally:
    client.close()
