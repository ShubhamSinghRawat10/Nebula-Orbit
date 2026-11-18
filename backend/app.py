"""Nebula API: authentication, learning activity, recommendations, and admin tools."""
from __future__ import annotations

import os
import re
import json
import math
import secrets
import csv
from datetime import datetime, timedelta, timezone
from functools import wraps
from pathlib import Path
from urllib.parse import urlparse
from zoneinfo import ZoneInfo

from bson import ObjectId, json_util
from dotenv import dotenv_values, load_dotenv
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, jwt_required
from pymongo import ASCENDING, MongoClient
from pymongo.errors import DuplicateKeyError, PyMongoError
from werkzeug.security import check_password_hash, generate_password_hash
from data_loader import import_curriculum
from performance_model import PerformanceModel

# Resolve this project's env file directly. In local development it is the source
# of truth even if an old terminal still has stale values; deployments continue
# to prefer secrets injected through the process environment.
ENV_FILE = Path(__file__).resolve().with_name(".env")
load_dotenv(ENV_FILE, override=os.getenv("NEBULA_ENV", "development").lower() != "production")


def utcnow():
    return datetime.now(timezone.utc)


def serialize(value):
    if isinstance(value, ObjectId):
        return str(value)
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, dict):
        return {k: serialize(v) for k, v in value.items() if k != "password_hash"}
    if isinstance(value, list):
        return [serialize(v) for v in value]
    return value


STUDY_GOALS = {
    "weak_topics": "Strengthen my weak topics",
    "foundations": "Build strong fundamentals",
    "explore_courses": "Explore my enrolled courses",
}
TRACK_FILE = Path(__file__).with_name("curriculum_tracks.csv")
try:
    with TRACK_FILE.open("r", encoding="utf-8-sig", newline="") as track_stream:
        CURRICULUM_TRACKS = {row["track_id"]: row for row in csv.DictReader(track_stream)}
except (OSError, KeyError):
    CURRICULUM_TRACKS = {"BTECH_CSE": {"track_id": "BTECH_CSE", "degree": "B.Tech", "branch": "Computer Science and Engineering", "display_name": "B.Tech · Computer Science & Engineering"}}
DEFAULT_TRACK = "BTECH_CSE"
STUDY_DAYS = ("mon", "tue", "wed", "thu", "fri", "sat", "sun")
DEFAULT_STUDY_DAYS = ["mon", "tue", "wed", "thu", "fri"]
SESSION_LENGTHS = (15, 25, 30, 45, 60)
MIN_DISTINCT_QUESTIONS_FOR_TOPIC_SIGNAL = 3


def question_signature(prompt):
    """Normalize a prompt so repeated attempts at one item do not inflate evidence."""
    return re.sub(r"\s+", " ", str(prompt or "")).strip().casefold()


def normalize_student_profile(profile, fallback=None):
    """Validate and normalize student study preferences across old/new accounts."""
    fallback = fallback if isinstance(fallback, dict) else {}
    mode = profile.get("goal_mode", fallback.get("goal_mode", "weak_topics"))
    if not isinstance(mode, str) or mode not in STUDY_GOALS:
        old_goal = str(profile.get("goal", fallback.get("goal", ""))).strip().casefold()
        mode = next((key for key, label in STUDY_GOALS.items() if old_goal == label.casefold()), "weak_topics")

    days = profile.get("available_days", fallback.get("available_days", DEFAULT_STUDY_DAYS))
    if not isinstance(days, list):
        raise ValueError("Choose at least one available study day.")
    days = list(dict.fromkeys(day for day in days if isinstance(day, str) and day in STUDY_DAYS))
    if not days:
        raise ValueError("Choose at least one available study day.")

    try:
        daily_minutes = int(profile.get("daily_minutes", fallback.get("daily_minutes", 60)))
        session_minutes = int(profile.get("preferred_session_minutes", fallback.get("preferred_session_minutes", 25)))
    except (TypeError, ValueError):
        raise ValueError("Study time and session length must be whole numbers.")
    if not 10 <= daily_minutes <= 480:
        raise ValueError("Daily study time must be between 10 and 480 minutes.")
    if session_minutes not in SESSION_LENGTHS:
        raise ValueError("Choose a supported session length.")

    track_id = str(profile.get("program_track", fallback.get("program_track", DEFAULT_TRACK))).strip().upper()
    if track_id not in CURRICULUM_TRACKS:
        raise ValueError("Choose a supported degree and branch.")
    track = CURRICULUM_TRACKS[track_id]
    return {
        "learning_track": track_id,
        "program_track": track_id,
        "degree": track.get("degree", "B.Tech"),
        "branch": track.get("branch", "Computer Science and Engineering"),
        "goal": STUDY_GOALS[mode],
        "goal_mode": mode,
        "level": str(profile.get("level", fallback.get("level", track.get("degree", "B.Tech"))))[:80],
        "daily_minutes": daily_minutes,
        "available_days": days,
        "preferred_session_minutes": session_minutes,
    }


def create_app(test_config=None):
    frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
    app = Flask(__name__, static_folder=frontend_dir, static_url_path="/assets")
    app.config.update(
        JWT_SECRET_KEY=os.getenv("JWT_SECRET_KEY", "dev-only-change-this-secret"),
        JWT_ACCESS_TOKEN_EXPIRES=timedelta(hours=12),
        MONGODB_URI=os.getenv("MONGODB_URI", "mongodb://127.0.0.1:27017/"),
        MONGODB_DB=os.getenv("MONGODB_DB", "nebula"),
        ADMIN_SIGNUP_KEY=os.getenv("ADMIN_SIGNUP_KEY", ""),
        FRONTEND_ORIGIN=os.getenv("FRONTEND_ORIGIN", "http://localhost:5173"),
        NEBULA_ENV=os.getenv("NEBULA_ENV", "development").lower(),
        MAX_CONTENT_LENGTH=1_048_576,
    )
    if test_config:
        app.config.update(test_config)

    demo_mode = os.getenv("NEBULA_DEMO_MODE", "false").lower() == "true"
    if app.config["NEBULA_ENV"] == "production" and not app.config.get("TESTING"):
        if demo_mode:
            raise RuntimeError("NEBULA_DEMO_MODE must be disabled in production.")
        parsed_mongo_uri = urlparse(app.config["MONGODB_URI"])
        if not parsed_mongo_uri.hostname or parsed_mongo_uri.hostname in {"localhost", "127.0.0.1"}:
            raise RuntimeError("Production requires a reachable managed or remote MongoDB URI.")
        if len(app.config["JWT_SECRET_KEY"]) < 32 or "replace-with" in app.config["JWT_SECRET_KEY"].lower():
            raise RuntimeError("Production requires a private JWT_SECRET_KEY with at least 32 characters.")
        if len(app.config["ADMIN_SIGNUP_KEY"]) < 24 or "replace-with" in app.config["ADMIN_SIGNUP_KEY"].lower():
            raise RuntimeError("Production requires a private ADMIN_SIGNUP_KEY with at least 24 characters.")
        frontend_origins = [origin.strip() for origin in str(app.config["FRONTEND_ORIGIN"]).split(",") if origin.strip()]
        if not frontend_origins or any(not origin.startswith("https://") for origin in frontend_origins):
            raise RuntimeError("Production FRONTEND_ORIGIN must use HTTPS.")
    allowed_origins = [origin.strip() for origin in str(app.config["FRONTEND_ORIGIN"]).split(",") if origin.strip()]
    CORS(app, resources={r"/api/*": {"origins": allowed_origins}})
    JWTManager(app)

    client_override = app.config.get("MONGODB_CLIENT")
    if client_override is not None:
        client = client_override
    elif demo_mode:
        import mongomock
        client = mongomock.MongoClient()
        app.logger.warning("Nebula demo mode uses local snapshot storage; use MongoDB for production or multiple app workers.")
    else:
        client = MongoClient(app.config["MONGODB_URI"], serverSelectionTimeoutMS=1500)
    db = client[app.config["MONGODB_DB"]]
    demo_store = Path(os.getenv("NEBULA_DEMO_STORE", os.path.join(os.path.dirname(__file__), ".demo_data.json")))
    if demo_mode and demo_store.exists():
        try:
            snapshot = json_util.loads(demo_store.read_text(encoding="utf-8"))
            for collection_name, documents in snapshot.items():
                if documents:
                    db[collection_name].insert_many(documents)
            app.logger.info("Restored Nebula demo data from the local snapshot.")
        except Exception:
            app.logger.exception("Could not restore the demo data snapshot; starting with an empty demo database.")
    users = db.users
    courses = db.courses
    topics_collection = db.topics
    prerequisites = db.prerequisites
    lessons = db.lessons
    enrollments = db.course_enrollments
    quizzes = db.quizzes
    attempts = db.attempts
    plans = db.study_plans
    study_session_completions = db.study_session_completions
    course_video_completions = db.course_video_completions
    course_completion_records = db.course_completion_records
    student_activity_days = db.student_activity_days
    app_metadata = db.app_metadata
    model_path = os.path.join(os.path.dirname(__file__), "performance_model.joblib")
    try:
        metrics_path = os.path.join(os.path.dirname(__file__), "performance_model_metrics.json")
        with open(metrics_path, encoding="utf-8") as metrics_file:
            model_metrics = json.load(metrics_file)
        if model_metrics.get("student_facing_eligible") and os.path.exists(model_path):
            performance_model = PerformanceModel.load(model_path)
            app.logger.info("Loaded next-assessment score model with validated student-facing lift.")
        else:
            performance_model = None
            app.logger.info("Score forecasts are disabled until the model beats the evaluation gate.")
    except Exception:
        performance_model = None
        app.logger.exception("Could not load the performance model; using score rules only.")

    @app.after_request
    def persist_demo_snapshot(response):
        if demo_mode and request.path.startswith("/api/") and request.method in {"POST", "PUT", "PATCH", "DELETE"}:
            try:
                snapshot = {name: list(db[name].find({})) for name in db.list_collection_names()}
                demo_store.parent.mkdir(parents=True, exist_ok=True)
                temporary_store = demo_store.with_suffix(demo_store.suffix + ".tmp")
                temporary_store.write_text(json_util.dumps(snapshot), encoding="utf-8")
                os.replace(temporary_store, demo_store)
            except Exception:
                app.logger.exception("Could not persist the Nebula demo data snapshot.")
        return response

    @app.after_request
    def security_headers(response):
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
        response.headers.setdefault(
            "Content-Security-Policy",
            "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; img-src 'self' data: https:; connect-src 'self'; "
            "object-src 'none'; base-uri 'self'; form-action 'self'; frame-ancestors 'none'",
        )
        if app.config["NEBULA_ENV"] == "production":
            response.headers.setdefault("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
        return response
    users.create_index([("email", ASCENDING)], unique=True)
    courses.create_index([("course_id", ASCENDING)], unique=True)
    enrollments.create_index([("student_id", ASCENDING), ("course_id", ASCENDING)], unique=True)
    study_session_completions.create_index([("student_id", ASCENDING), ("session_id", ASCENDING)], unique=True)
    study_session_completions.create_index([("student_id", ASCENDING), ("course_id", ASCENDING), ("topic", ASCENDING), ("completed_at", ASCENDING)])
    course_video_completions.create_index([("student_id", ASCENDING), ("course_id", ASCENDING), ("topic_id", ASCENDING)], unique=True)
    course_completion_records.create_index([("student_id", ASCENDING), ("course_id", ASCENDING)], unique=True)
    student_activity_days.create_index([("student_id", ASCENDING), ("activity_date", ASCENDING)], unique=True)
    app_metadata.update_one(
        {"_id": "pilot_activity_tracking_started_at"},
        {"$setOnInsert": {"started_at": utcnow()}},
        upsert=True,
    )
    pilot_tracking_started_at = app_metadata.find_one({"_id": "pilot_activity_tracking_started_at"})["started_at"]

    if demo_mode:
        # Pick up replaced CSV curriculum files on the next demo server start.
        import_curriculum(db, os.path.dirname(__file__))
    if demo_mode and quizzes.count_documents({}) == 0:
        quizzes.insert_many([
            {"title": "DSA baseline diagnostic", "course_id": "DSA", "topic": "Data Structures & Algorithms - Fundamentals & Core Concepts", "difficulty": "mixed", "published": True, "created_at": utcnow(), "questions": [
                {"prompt": "Which structure removes the most recently added item first?", "topic": "Data Structures & Algorithms - Data Structures & Types", "options": ["Queue", "Stack", "Graph", "Hash table"], "answer_index": 1, "explanation": "A stack follows last-in, first-out order."},
                {"prompt": "Which structure is a natural fit for processing jobs in arrival order?", "topic": "Data Structures & Algorithms - Data Structures & Types", "options": ["Stack", "Queue", "Binary search tree", "Hash set"], "answer_index": 1, "explanation": "A queue processes the earliest enqueued item first."},
                {"prompt": "For a sorted array, what is the time complexity of binary search?", "topic": "Data Structures & Algorithms - Algorithms & Control Logic", "options": ["O(1)", "O(log n)", "O(n)", "O(n²)"], "answer_index": 1, "explanation": "Each comparison removes about half of the remaining search range."},
                {"prompt": "Why is a linked list usually a poor fit for repeatedly reading item i by index?", "topic": "Data Structures & Algorithms - Algorithms & Control Logic", "options": ["It stores no values", "It requires walking nodes from the head", "It sorts itself after each insert", "It only supports numeric data"], "answer_index": 1, "explanation": "A linked list has sequential access, so reaching an index takes traversal."},
                {"prompt": "Which structure is commonly used to check whether brackets are properly nested?", "topic": "Data Structures & Algorithms - Primary Protocols & Operations", "options": ["Stack", "Queue", "Heap", "Array only"], "answer_index": 0, "explanation": "The most recently opened bracket must be matched first, which suits a stack."},
                {"prompt": "A breadth-first traversal of a graph typically uses which structure to track the frontier?", "topic": "Data Structures & Algorithms - Algorithms & Control Logic", "options": ["Queue", "Stack only", "Sorted array", "Hash table only"], "answer_index": 0, "explanation": "A queue visits discovered nodes in first-in, first-out order."},
                {"prompt": "On average, which operation is a hash table designed to make fast?", "topic": "Data Structures & Algorithms - Optimization & Performance", "options": ["Lookup by key", "Visit every item in sorted order", "Find the middle node of a linked list", "Sort all values"], "answer_index": 0, "explanation": "Hash tables typically provide average constant-time key lookup; worst cases can be slower."},
                {"prompt": "What does an array usually provide for direct access by index?", "topic": "Data Structures & Algorithms - Optimization & Performance", "options": ["O(1) access", "O(log n) access", "O(n) access", "O(n²) access"], "answer_index": 0, "explanation": "An array computes an element's position from its index, enabling constant-time access."},
            ]},
            {"title": "Python baseline diagnostic", "course_id": "PY", "topic": "Python for Data Science - Fundamentals & Core Concepts", "difficulty": "mixed", "published": True, "created_at": utcnow(), "questions": [
                {"prompt": "Which built-in collection is ordered and can be changed after creation?", "topic": "Python for Data Science - Data Structures & Types", "options": ["List", "Tuple", "String", "Frozen set"], "answer_index": 0, "explanation": "Lists are ordered and mutable."},
                {"prompt": "Which collection is intended to keep unique values?", "topic": "Python for Data Science - Data Structures & Types", "options": ["List", "Tuple", "Set", "String"], "answer_index": 2, "explanation": "A set stores unique elements."},
                {"prompt": "Which Python type stores key-value pairs?", "topic": "Python for Data Science - Data Structures & Types", "options": ["Dictionary", "Tuple", "Range", "Boolean"], "answer_index": 0, "explanation": "A dictionary maps keys to values."},
                {"prompt": "What does len([3, 8, 2]) return?", "topic": "Python for Data Science - Implementation & Syntax", "options": ["2", "3", "8", "13"], "answer_index": 1, "explanation": "The list contains three items."},
                {"prompt": "What does tuple immutability mean?", "topic": "Python for Data Science - Data Structures & Types", "options": ["Its elements cannot be reassigned in place", "It cannot contain strings", "It automatically sorts values", "It allows no duplicate values"], "answer_index": 0, "explanation": "A tuple cannot be changed in place after it is created."},
                {"prompt": "What does values.get('missing', 0) return when the key is absent?", "topic": "Python for Data Science - Primary Protocols & Operations", "options": ["None always", "0", "False", "A KeyError"], "answer_index": 1, "explanation": "dict.get returns the supplied default when the key is missing."},
                {"prompt": "What is the result of set([1, 1, 2]) in terms of number of elements?", "topic": "Python for Data Science - Data Structures & Types", "options": ["1", "2", "3", "It raises an error"], "answer_index": 1, "explanation": "Converting to a set removes duplicate values, leaving two elements."},
                {"prompt": "Which expression creates an empty dictionary?", "topic": "Python for Data Science - Implementation & Syntax", "options": ["{}", "[]", "()", "set()"], "answer_index": 0, "explanation": "Curly braces with no entries create an empty dictionary; set() creates an empty set."},
            ]},
        ])

    if demo_mode:
        from starter_quizzes import starter_quizzes
        for starter_quiz in starter_quizzes():
            existing_quiz = quizzes.find_one({"course_id": starter_quiz["course_id"]})
            if not existing_quiz:
                quizzes.insert_one(starter_quiz)
            elif (existing_quiz.get("source") == "nebula_starter"
                  and existing_quiz.get("title") == starter_quiz["title"]
                  and len(existing_quiz.get("questions", [])) < len(starter_quiz["questions"])):
                # Upgrade only source-owned Nebula diagnostics, never admin-edited quizzes.
                quizzes.update_one(
                    {"_id": existing_quiz["_id"], "title": starter_quiz["title"]},
                    {"$set": {"questions": starter_quiz["questions"], "source": "nebula_starter"}},
                )

    @app.get("/")
    def home():
        return send_from_directory(app.static_folder, "index.html")

    def api_error(message, status=400):
        return jsonify({"error": message}), status

    def normalize_course_topics(value):
        if not isinstance(value, list) or not value or len(value) > 60:
            raise ValueError("Add between 1 and 60 course topics.")
        topics = []
        seen = set()
        for item in value:
            if not isinstance(item, str):
                raise ValueError("Each topic must be text.")
            name = item.strip()
            if not name or len(name) > 160:
                raise ValueError("Topic names must contain 1 to 160 characters.")
            key = name.casefold()
            if key in seen:
                raise ValueError("Course topic names must be unique.")
            seen.add(key)
            topics.append(name)
        return topics

    def parse_course_hours(value):
        if isinstance(value, bool):
            raise ValueError("Estimated hours must be a whole number from 1 to 1000.")
        try:
            hours = int(value)
        except (TypeError, ValueError):
            raise ValueError("Estimated hours must be a whole number from 1 to 1000.")
        if str(value).strip() != str(hours) or not 1 <= hours <= 1000:
            raise ValueError("Estimated hours must be a whole number from 1 to 1000.")
        return hours

    def course_has_activity(course_id, topic_ids):
        dependency_queries = [
            (lessons, {"course_id": course_id}),
            (enrollments, {"course_id": course_id}),
            (quizzes, {"course_id": course_id}),
            (attempts, {"course_id": course_id}),
            (plans, {"tasks.course_id": course_id}),
            (db.dataset_interactions, {"course_id": course_id}),
        ]
        if any(collection.count_documents(query) for collection, query in dependency_queries):
            return True
        if topic_ids and prerequisites.count_documents({"$or": [
            {"topic_id": {"$in": topic_ids}},
            {"prerequisite_topic_id": {"$in": topic_ids}},
        ]}):
            return True
        return False

    def make_course_topic_docs(course_id, topic_names, estimated_hours):
        per_topic_hours = max(1, math.ceil(estimated_hours / len(topic_names)))
        return [{
            "topic_id": f"{course_id}_T{index + 1}",
            "course_id": course_id,
            "topic_name": name,
            "difficulty_level": "Beginner",
            "estimated_hours": per_topic_hours,
            "source": "admin",
        } for index, name in enumerate(topic_names)]

    def normalize_program_tracks(value):
        if not isinstance(value, list):
            raise ValueError("Choose at least one degree or branch track for this course.")
        normalized = list(dict.fromkeys(str(track).strip().upper() for track in value if str(track).strip()))
        if not normalized or any(track not in CURRICULUM_TRACKS for track in normalized):
            raise ValueError("Choose one or more supported degree or branch tracks.")
        return normalized

    def current_user():
        identity = get_jwt_identity()
        try:
            user = users.find_one({"_id": ObjectId(identity)})
        except Exception:
            user = None
        return user

    def record_student_activity(user_id, event_type):
        """Store one privacy-light activity record per student and UTC day."""
        now = utcnow()
        student_activity_days.update_one(
            {"student_id": user_id, "activity_date": now.date().isoformat()},
            {"$setOnInsert": {"student_id": user_id, "activity_date": now.date().isoformat(), "first_activity_at": now},
             "$set": {"last_activity_at": now}, "$addToSet": {"event_types": event_type}},
            upsert=True,
        )

    def user_is_active(user):
        # Accounts created before status management are active by default.
        return user is not None and user.get("status", "active") == "active"

    def student_can_access_course(user, course_id):
        if not user or user.get("role") != "student":
            return True
        profile = normalize_student_profile(user.get("profile", {}))
        return bool(courses.find_one({"course_id": str(course_id).upper(), "program_tracks": profile["program_track"]}, {"_id": 1}))

    def student_track_course_ids(user):
        profile = normalize_student_profile(user.get("profile", {}))
        return [row["course_id"] for row in courses.find({"program_tracks": profile["program_track"]}, {"course_id": 1})]

    def role_required(*roles):
        def decorator(fn):
            @wraps(fn)
            @jwt_required()
            def wrapped(*args, **kwargs):
                user = current_user()
                if not user or user.get("role") not in roles:
                    return api_error("You do not have permission to do that.", 403)
                if not user_is_active(user):
                    return api_error("This account is suspended. Contact an administrator.", 403)
                return fn(*args, **kwargs)
            return wrapped
        return decorator

    @app.get("/api/health")
    def health():
        try:
            client.admin.command("ping")
            return jsonify({"status": "ok", "database": "connected"})
        except PyMongoError:
            return jsonify({"status": "degraded", "database": "unavailable"}), 503

    @app.get("/api/curriculum-tracks")
    def curriculum_tracks():
        return jsonify({"tracks": [
            {"track_id": track_id, "degree": row.get("degree", ""), "branch": row.get("branch", ""),
             "display_name": row.get("display_name", track_id), "source_scope": row.get("source_scope", "")}
            for track_id, row in CURRICULUM_TRACKS.items()
        ]})

    @app.post("/api/auth/register")
    def register():
        body = request.get_json(silent=True) or {}
        name = str(body.get("name", "")).strip()
        email = str(body.get("email", "")).strip().lower()
        raw_password = body.get("password", "")
        password = raw_password if isinstance(raw_password, str) else ""
        role = str(body.get("role", "student")).lower()
        if len(name) < 2 or len(name) > 80:
            return api_error("Enter a name between 2 and 80 characters.")
        if len(email) > 254 or not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email):
            return api_error("Enter a valid email address.")
        if len(password) < 10 or len(password) > 128:
            return api_error("Password must be between 10 and 128 characters long.")
        if role not in ("student", "admin"):
            return api_error("Choose a valid account type.")
        if role == "admin":
            supplied_key = str(body.get("admin_signup_key", ""))
            expected_key = app.config["ADMIN_SIGNUP_KEY"]
            if not app.config.get("TESTING") and app.config["NEBULA_ENV"] != "production":
                # In local development, read the project's .env at request time
                # so edits take effect even if a stale Flask process is running.
                expected_key = dotenv_values(ENV_FILE).get("ADMIN_SIGNUP_KEY") or expected_key
            if not expected_key or supplied_key != expected_key:
                return api_error("Admin registration requires a valid setup key.", 403)
        profile = body.get("profile", {}) if isinstance(body.get("profile", {}), dict) else {}
        try:
            normalized_profile = normalize_student_profile(profile)
        except ValueError as error:
            return api_error(str(error))
        user = {
            "name": name,
            "email": email,
            "password_hash": generate_password_hash(password),
            "role": role,
            "status": "active",
            "profile": normalized_profile if role == "student" else {},
            "created_at": utcnow(),
        }
        try:
            result = users.insert_one(user)
        except DuplicateKeyError:
            return api_error("An account with this email already exists.", 409)
        token = create_access_token(identity=str(result.inserted_id), additional_claims={"role": role})
        user["_id"] = result.inserted_id
        return jsonify({"access_token": token, "user": serialize(user)}), 201

    @app.post("/api/auth/login")
    def login():
        body = request.get_json(silent=True) or {}
        email = str(body.get("email", "")).strip().lower()
        raw_password = body.get("password", "")
        password = raw_password if isinstance(raw_password, str) else ""
        if len(password) > 128:
            return api_error("Email or password is incorrect.", 401)
        user = users.find_one({"email": email})
        if not user or not check_password_hash(user.get("password_hash", ""), password):
            return api_error("Email or password is incorrect.", 401)
        if not user_is_active(user):
            return api_error("This account is suspended. Contact an administrator.", 403)
        token = create_access_token(identity=str(user["_id"]), additional_claims={"role": user["role"]})
        if user.get("role") == "student":
            record_student_activity(user["_id"], "app_open")
        return jsonify({"access_token": token, "user": serialize(user)})

    @app.get("/api/auth/me")
    @jwt_required()
    def me():
        user = current_user()
        if not user or not user_is_active(user):
            return api_error("Account not found.", 404)
        if user.get("role") == "student":
            record_student_activity(user["_id"], "app_open")
        return jsonify({"user": serialize(user)})

    @app.patch("/api/auth/profile")
    @role_required("student")
    def update_profile():
        user = current_user()
        body = request.get_json(silent=True) or {}
        profile = body.get("profile", {})
        if not isinstance(profile, dict):
            return api_error("Profile must be an object.")
        try:
            updated = normalize_student_profile(profile, user.get("profile", {}))
        except ValueError as error:
            return api_error(str(error))
        users.update_one({"_id": user["_id"]}, {"$set": {"profile": updated}})
        user["profile"] = updated
        return jsonify({"user": serialize(user)})

    @app.get("/api/courses")
    @jwt_required()
    def list_courses():
        user = current_user()
        if not user_is_active(user):
            return api_error("This account is suspended.", 403)
        query = {}
        if user.get("role") == "student":
            profile = normalize_student_profile(user.get("profile", {}))
            query["program_tracks"] = profile["program_track"]
        cursor = courses.find(query).sort("title", ASCENDING)
        return jsonify({"courses": serialize(list(cursor))})

    @app.get("/api/enrollments")
    @role_required("student")
    def list_enrollments():
        user = current_user()
        rows = list(enrollments.find({"student_id": user["_id"]}).sort("created_at", -1))
        return jsonify({"course_ids": [row["course_id"] for row in rows]})

    @app.post("/api/enrollments/<course_id>")
    @role_required("student")
    def enroll_in_course(course_id):
        user = current_user()
        course_id = course_id.upper()
        if not student_can_access_course(user, course_id):
            return api_error("Course not found.", 404)
        enrollments.update_one({"student_id": user["_id"], "course_id": course_id}, {"$setOnInsert": {"student_id": user["_id"], "course_id": course_id, "created_at": utcnow()}}, upsert=True)
        return jsonify({"enrolled": True, "course_id": course_id})

    @app.delete("/api/enrollments/<course_id>")
    @role_required("student")
    def unenroll_from_course(course_id):
        user = current_user()
        course_id = course_id.upper()
        enrollments.delete_one({"student_id": user["_id"], "course_id": course_id})
        return jsonify({"enrolled": False, "course_id": course_id})

    @app.get("/api/courses/<course_id>/topics")
    @jwt_required()
    def list_course_topics(course_id):
        user = current_user()
        if not user_is_active(user):
            return api_error("This account is suspended.", 403)
        course_id = course_id.upper()
        if not student_can_access_course(user, course_id):
            return api_error("Course not found.", 404)
        rows = list(topics_collection.find({"course_id": course_id}).sort("topic_id", ASCENDING))
        for topic in rows:
            edges = prerequisites.find({"topic_id": topic["topic_id"]})
            topic["prerequisites"] = []
            for edge in edges:
                required = topics_collection.find_one({"topic_id": edge["prerequisite_topic_id"]})
                if required:
                    topic["prerequisites"].append({"topic_id": required["topic_id"], "topic_name": required["topic_name"], "type": edge["prerequisite_type"]})
        return jsonify({"topics": serialize(rows)})

    @app.get("/api/courses/<course_id>/video-progress")
    @role_required("student")
    def course_video_progress(course_id):
        user = current_user()
        course_id = course_id.upper()
        if not student_can_access_course(user, course_id):
            return api_error("Course not found.", 404)
        topic_ids = [row["topic_id"] for row in topics_collection.find({"course_id": course_id}, {"topic_id": 1})]
        rows = list(course_video_completions.find({"student_id": user["_id"], "course_id": course_id}))
        completed_ids = {row["topic_id"] for row in rows}
        record = course_completion_records.find_one({"student_id": user["_id"], "course_id": course_id})
        return jsonify({"completed_topic_ids": sorted(completed_ids), "total_topics": len(topic_ids), "completed_count": len(completed_ids), "course_completed_at": serialize(record.get("completed_at")) if record else None, "revision_due_at": serialize(record.get("revision_due_at")) if record else None})

    @app.post("/api/courses/<course_id>/topics/<topic_id>/video-complete")
    @role_required("student")
    def complete_course_video(course_id, topic_id):
        user = current_user()
        course_id = course_id.upper()
        if not student_can_access_course(user, course_id):
            return api_error("Course not found.", 404)
        topic = topics_collection.find_one({"course_id": course_id, "topic_id": topic_id})
        if not topic:
            return api_error("Topic not found in this course.", 404)
        completed_at = utcnow()
        course_video_completions.update_one(
            {"student_id": user["_id"], "course_id": course_id, "topic_id": topic_id},
            {"$setOnInsert": {"student_id": user["_id"], "course_id": course_id, "topic_id": topic_id, "topic_name": topic.get("topic_name", ""), "completed_at": completed_at}},
            upsert=True,
        )
        topic_ids = [row["topic_id"] for row in topics_collection.find({"course_id": course_id}, {"topic_id": 1})]
        completed_rows = list(course_video_completions.find({"student_id": user["_id"], "course_id": course_id}))
        completed_ids = {row["topic_id"] for row in completed_rows}
        record = None
        if topic_ids and set(topic_ids).issubset(completed_ids):
            final_marked_at = max(row["completed_at"] for row in completed_rows if row["topic_id"] in topic_ids)
            revision_due_at = final_marked_at + timedelta(days=7)
            course_completion_records.update_one(
                {"student_id": user["_id"], "course_id": course_id},
                {"$setOnInsert": {"student_id": user["_id"], "course_id": course_id, "completed_at": final_marked_at, "revision_due_at": revision_due_at, "created_at": completed_at}},
                upsert=True,
            )
            record = course_completion_records.find_one({"student_id": user["_id"], "course_id": course_id})
        record_student_activity(user["_id"], "course_video_completion")
        return jsonify({"completed": True, "topic_id": topic_id, "completed_topic_ids": sorted(completed_ids), "total_topics": len(topic_ids), "completed_count": len(completed_ids), "course_completed_at": record.get("completed_at") if record else None, "revision_due_at": record.get("revision_due_at") if record else None})

    @app.get("/api/courses/<course_id>/lessons")
    @jwt_required()
    def list_course_lessons(course_id):
        user = current_user()
        if not user_is_active(user):
            return api_error("This account is suspended.", 403)
        course_id = course_id.upper()
        if not student_can_access_course(user, course_id):
            return api_error("Course not found.", 404)
        query = {"course_id": course_id}
        if user.get("role") != "admin":
            query["published"] = True
        rows = list(lessons.find(query).sort([("position", ASCENDING), ("title", ASCENDING)]))
        if user.get("role") == "student":
            completed = {item["lesson_id"] for item in db.lesson_completions.find({"student_id": user["_id"]})}
            for lesson in rows:
                lesson["completed"] = str(lesson["_id"]) in completed
        return jsonify({"lessons": serialize(rows)})

    def clean_lesson(body, existing=None):
        body = body if isinstance(body, dict) else {}
        existing = existing or {}
        course_id = str(body.get("course_id", existing.get("course_id", ""))).strip().upper()
        topic_id = str(body.get("topic_id", existing.get("topic_id", ""))).strip()
        title = str(body.get("title", existing.get("title", ""))).strip()
        summary = str(body.get("summary", existing.get("summary", ""))).strip()
        content = str(body.get("content", existing.get("content", ""))).strip()
        video_url = str(body.get("video_url", existing.get("video_url", ""))).strip()
        published = body.get("published", existing.get("published", False))
        if type(published) is not bool:
            return None, "Lesson visibility must be true or false."
        if not courses.find_one({"course_id": course_id}):
            return None, "Choose an existing course."
        topic = topics_collection.find_one({"topic_id": topic_id, "course_id": course_id}) if topic_id else None
        if not title or len(title) > 160 or not topic:
            return None, "Choose a course topic and enter a lesson title (up to 160 characters)."
        if len(summary) > 500 or len(content) > 20000:
            return None, "Summary must be under 500 characters and lesson content under 20,000 characters."
        if video_url and not re.match(r"^https?://", video_url, re.IGNORECASE):
            return None, "Video URL must start with http:// or https://."
        try:
            position = max(0, min(10000, int(body.get("position", existing.get("position", 0)) or 0)))
        except (TypeError, ValueError):
            return None, "Lesson order must be a whole number from 0 to 10000."
        return {"course_id": course_id, "topic_id": topic_id, "topic_name": topic["topic_name"], "title": title, "summary": summary, "content": content, "video_url": video_url[:1000], "position": position, "published": published}, None

    @app.get("/api/admin/lessons")
    @role_required("admin")
    def admin_list_lessons():
        rows = list(lessons.find({}).sort([("course_id", ASCENDING), ("position", ASCENDING), ("title", ASCENDING)]))
        return jsonify({"lessons": serialize(rows)})

    @app.post("/api/admin/lessons")
    @role_required("admin")
    def admin_create_lesson():
        doc, error = clean_lesson(request.get_json(silent=True) or {})
        if error:
            return api_error(error)
        doc.update({"created_at": utcnow(), "updated_at": utcnow()})
        result = lessons.insert_one(doc)
        doc["_id"] = result.inserted_id
        return jsonify({"lesson": serialize(doc)}), 201

    @app.put("/api/admin/lessons/<lesson_id>")
    @role_required("admin")
    def admin_edit_lesson(lesson_id):
        try:
            lesson = lessons.find_one({"_id": ObjectId(lesson_id)})
        except Exception:
            lesson = None
        if not lesson:
            return api_error("Lesson not found.", 404)
        doc, error = clean_lesson(request.get_json(silent=True) or {}, lesson)
        if error:
            return api_error(error)
        doc["updated_at"] = utcnow()
        lessons.update_one({"_id": lesson["_id"]}, {"$set": doc})
        return jsonify({"lesson": serialize(lessons.find_one({"_id": lesson["_id"]}))})

    @app.delete("/api/admin/lessons/<lesson_id>")
    @role_required("admin")
    def admin_delete_lesson(lesson_id):
        try:
            result = lessons.delete_one({"_id": ObjectId(lesson_id)})
        except Exception:
            result = None
        if not result or not result.deleted_count:
            return api_error("Lesson not found.", 404)
        db.lesson_completions.delete_many({"lesson_id": lesson_id})
        return jsonify({"deleted": True})

    @app.get("/api/admin/students")
    @role_required("admin")
    def admin_list_students():
        search = str(request.args.get("q", "")).strip()[:100]
        query = {"role": "student"}
        if search:
            safe_search = re.escape(search)
            query["$or"] = [{"name": {"$regex": safe_search, "$options": "i"}}, {"email": {"$regex": safe_search, "$options": "i"}}]
        rows = list(users.find(query).sort("created_at", -1).limit(200))
        student_rows = []
        for student in rows:
            latest = list(attempts.find({"student_id": student["_id"]}).sort("created_at", -1).limit(1))
            student_rows.append({"id": str(student["_id"]), "name": student.get("name", ""), "email": student.get("email", ""), "status": student.get("status", "active"), "profile": student.get("profile", {}), "created_at": student.get("created_at"), "attempt_count": attempts.count_documents({"student_id": student["_id"]}), "last_activity": latest[0].get("created_at") if latest else None})
        return jsonify({"students": serialize(student_rows), "limit": 200})

    @app.patch("/api/admin/students/<student_id>/status")
    @role_required("admin")
    def admin_set_student_status(student_id):
        status = (request.get_json(silent=True) or {}).get("status")
        if status not in ("active", "suspended"):
            return api_error("Status must be active or suspended.")
        try:
            target_id = ObjectId(student_id)
        except Exception:
            return api_error("Student not found.", 404)
        result = users.update_one({"_id": target_id, "role": "student"}, {"$set": {"status": status}})
        if not result.matched_count:
            return api_error("Student not found.", 404)
        return jsonify({"id": student_id, "status": status})

    @app.post("/api/courses")
    @role_required("admin")
    def create_course():
        body = request.get_json(silent=True) or {}
        title = str(body.get("title", "")).strip()
        course_id = str(body.get("course_id", "")).strip().upper()
        if not title or len(title) > 120 or not course_id or not re.fullmatch(r"[A-Z0-9][A-Z0-9_-]{0,39}", course_id):
            return api_error("Course title and course ID are required.")
        try:
            topic_names = normalize_course_topics(body.get("topics"))
            estimated_hours = parse_course_hours(body.get("estimated_hours", 1))
            program_tracks = normalize_program_tracks(body.get("program_tracks"))
        except ValueError as error:
            return api_error(str(error))
        topic_docs = make_course_topic_docs(course_id, topic_names, estimated_hours)
        if topics_collection.count_documents({"topic_id": {"$in": [topic["topic_id"] for topic in topic_docs]}}):
            return api_error("Topic IDs for that course already exist.", 409)
        creation_token = secrets.token_hex(16)
        for topic in topic_docs:
            topic["_creation_token"] = creation_token
        doc = {
            "course_id": course_id,
            "title": title[:120],
            "subject": str(body.get("subject", "General"))[:80],
            "level": str(body.get("level", "Beginner"))[:60],
            "description": str(body.get("description", ""))[:2000],
            "estimated_hours": estimated_hours,
            "topics": topic_names,
            "topic_ids": [topic["topic_id"] for topic in topic_docs],
            "program_tracks": program_tracks,
            "created_at": utcnow(),
        }
        try:
            result = courses.insert_one(doc)
        except DuplicateKeyError:
            return api_error("That course ID already exists.", 409)
        try:
            topics_collection.insert_many(topic_docs)
            topics_collection.update_many({"_creation_token": creation_token}, {"$unset": {"_creation_token": ""}})
        except Exception:
            courses.delete_one({"_id": result.inserted_id})
            topics_collection.delete_many({"_creation_token": creation_token})
            app.logger.exception("Could not create course topics; rolled back course creation.")
            return api_error("The course could not be saved. Please retry.", 500)
        doc["_id"] = result.inserted_id
        return jsonify({"course": serialize(doc)}), 201

    @app.put("/api/courses/<course_id>")
    @role_required("admin")
    def edit_course(course_id):
        body = request.get_json(silent=True) or {}
        allowed = {"title", "subject", "level", "description", "estimated_hours", "topics", "program_tracks"}
        changes = {k: body[k] for k in allowed if k in body}
        if not changes:
            return api_error("No course fields were provided.")
        course_id = course_id.upper()
        doc = courses.find_one({"course_id": course_id})
        if not doc:
            return api_error("Course not found.", 404)
        for field, limit in (("title", 120), ("subject", 80), ("level", 60), ("description", 2000)):
            if field in changes:
                if not isinstance(changes[field], str) or not changes[field].strip() or len(changes[field].strip()) > limit:
                    return api_error(f"{field.title()} must contain 1 to {limit} characters.")
                changes[field] = changes[field].strip()
        if "estimated_hours" in changes:
            try:
                changes["estimated_hours"] = parse_course_hours(changes["estimated_hours"])
            except ValueError as error:
                return api_error(str(error))
        if "program_tracks" in changes:
            try:
                changes["program_tracks"] = normalize_program_tracks(changes["program_tracks"])
            except ValueError as error:
                return api_error(str(error))
        if "topics" in changes:
            try:
                topic_names = normalize_course_topics(changes["topics"])
            except ValueError as error:
                return api_error(str(error))
            old_names = doc.get("topics", [])
            if topic_names != old_names:
                old_topic_ids = doc.get("topic_ids") or [row["topic_id"] for row in topics_collection.find({"course_id": course_id}, {"topic_id": 1})]
                if course_has_activity(course_id, old_topic_ids):
                    return api_error("Topics cannot change after lessons, quizzes, enrollments, or study activity use this course.", 409)
                if old_topic_ids:
                    prerequisites.delete_many({"$or": [
                        {"topic_id": {"$in": old_topic_ids}},
                        {"prerequisite_topic_id": {"$in": old_topic_ids}},
                    ]})
                topics_collection.delete_many({"course_id": course_id})
                topic_docs = make_course_topic_docs(course_id, topic_names, changes.get("estimated_hours", doc.get("estimated_hours", 1)))
                try:
                    topics_collection.insert_many(topic_docs)
                except Exception:
                    app.logger.exception("Could not replace course topics for %s.", course_id)
                    return api_error("Course topics could not be updated.", 500)
                changes["topics"] = topic_names
                changes["topic_ids"] = [topic["topic_id"] for topic in topic_docs]
        courses.update_one({"course_id": course_id}, {"$set": changes})
        doc = courses.find_one({"course_id": course_id})
        return (jsonify({"course": serialize(doc)}), 200) if doc else api_error("Course not found.", 404)

    @app.delete("/api/courses/<course_id>")
    @role_required("admin")
    def delete_course(course_id):
        course_id = course_id.upper()
        course = courses.find_one({"course_id": course_id})
        if not course:
            return api_error("Course not found.", 404)
        topic_ids = course.get("topic_ids") or [row["topic_id"] for row in topics_collection.find({"course_id": course_id}, {"topic_id": 1})]
        if course_has_activity(course_id, topic_ids):
            return api_error("This course has lessons, quizzes, enrollments, or student activity and cannot be deleted.", 409)
        if topic_ids:
            prerequisites.delete_many({"$or": [
                {"topic_id": {"$in": topic_ids}},
                {"prerequisite_topic_id": {"$in": topic_ids}},
            ]})
        topics_collection.delete_many({"course_id": course_id})
        result = courses.delete_one({"course_id": course_id})
        return (jsonify({"deleted": True}), 200) if result.deleted_count else api_error("Course not found.", 404)

    @app.get("/api/quizzes")
    @jwt_required()
    def list_quizzes():
        user = current_user()
        if not user_is_active(user):
            return api_error("This account is suspended.", 403)
        is_student = user.get("role") == "student"
        query = {"published": True, "content_review_status": {"$ne": "review_revisions_needed"}} if is_student else {}
        if is_student:
            profile = normalize_student_profile(user.get("profile", {}))
            matching_courses = [course["course_id"] for course in courses.find({"program_tracks": profile["program_track"]}, {"course_id": 1})]
            query["course_id"] = {"$in": matching_courses}
        items = list(quizzes.find(query).sort("title", ASCENDING))
        if is_student:
            for quiz in items:
                if (quiz.get("seed_key", "").startswith("nebula-practice-")
                        or quiz.get("source") == "Nebula curated practice v1"):
                    quiz.setdefault("content_review_status", "instructor_review_pending")
                kind = str(quiz.get("assessment_type", "")).strip().lower()
                if kind not in {"baseline", "topic_practice"}:
                    title = str(quiz.get("title", "")).lower()
                    kind = "baseline" if "baseline" in title or "diagnostic" in title else "topic_practice"
                quiz["assessment_type"] = kind
                quiz["questions"] = [{k: v for k, v in question.items() if k != "answer_index"} for question in quiz.get("questions", [])]
        return jsonify({"quizzes": serialize(items)})

    @app.get("/api/quizzes/<quiz_id>")
    @jwt_required()
    def get_quiz(quiz_id):
        user = current_user()
        if not user_is_active(user):
            return api_error("This account is suspended.", 403)
        try:
            quiz = quizzes.find_one({"_id": ObjectId(quiz_id)})
        except Exception:
            quiz = None
        if not quiz or (user.get("role") == "student" and (not quiz.get("published") or quiz.get("content_review_status") == "review_revisions_needed")):
            return api_error("Quiz not found.", 404)
        if not student_can_access_course(user, quiz.get("course_id", "")):
            return api_error("Quiz not found.", 404)
        if user.get("role") == "student":
            if (quiz.get("seed_key", "").startswith("nebula-practice-")
                    or quiz.get("source") == "Nebula curated practice v1"):
                quiz.setdefault("content_review_status", "instructor_review_pending")
            kind = str(quiz.get("assessment_type", "")).strip().lower()
            if kind not in {"baseline", "topic_practice"}:
                title = str(quiz.get("title", "")).lower()
                kind = "baseline" if "baseline" in title or "diagnostic" in title else "topic_practice"
            quiz["assessment_type"] = kind
            quiz["questions"] = [{k: v for k, v in question.items() if k != "answer_index"} for question in quiz.get("questions", [])]
        return jsonify({"quiz": serialize(quiz)})

    @app.post("/api/quizzes")
    @role_required("admin")
    def create_quiz():
        body = request.get_json(silent=True) or {}
        title = str(body.get("title", "")).strip()
        questions = body.get("questions", [])
        if not title or not isinstance(questions, list) or not questions:
            return api_error("Quiz title and at least one question are required.")
        cleaned = []
        for question in questions:
            if not isinstance(question, dict) or not str(question.get("prompt", "")).strip() or not isinstance(question.get("options"), list) or len(question["options"]) < 2:
                return api_error("Every question needs a prompt and at least two choices.")
            options = [str(option).strip()[:300] for option in question["options"][:8]]
            answer = question.get("answer_index")
            if type(answer) is not int or answer < 0 or answer >= len(options) or any(not option for option in options):
                return api_error("Each question needs a valid answer index.")
            cleaned.append({"prompt": str(question["prompt"]).strip()[:1000], "topic": str(question.get("topic", "")).strip()[:160], "options": options, "answer_index": answer, "explanation": str(question.get("explanation", ""))[:1000]})
        doc = {"title": title[:120], "course_id": str(body.get("course_id", ""))[:40], "topic": str(body.get("topic", "General"))[:100], "difficulty": str(body.get("difficulty", "medium")), "questions": cleaned, "published": bool(body.get("published", False)), "created_at": utcnow(), "updated_at": utcnow()}
        result = quizzes.insert_one(doc)
        doc["_id"] = result.inserted_id
        return jsonify({"quiz": serialize(doc)}), 201

    @app.put("/api/quizzes/<quiz_id>")
    @role_required("admin")
    def edit_quiz(quiz_id):
        body = request.get_json(silent=True) or {}
        changes = {k: body[k] for k in ("title", "course_id", "topic", "difficulty", "questions", "published") if k in body}
        if not changes:
            return api_error("No quiz fields were provided.")
        if "questions" in changes:
            question_list = changes["questions"]
            if not isinstance(question_list, list) or not question_list:
                return api_error("Quiz needs at least one question.")
            cleaned = []
            for question in question_list:
                answer = question.get("answer_index") if isinstance(question, dict) else None
                if not isinstance(question, dict) or not str(question.get("prompt", "")).strip() or not isinstance(question.get("options"), list) or len(question["options"]) < 2:
                    return api_error("Each question needs a prompt, two choices and a valid answer.")
                options = [str(option).strip()[:300] for option in question["options"][:8]]
                if type(answer) is not int or answer < 0 or answer >= len(options) or any(not option for option in options):
                    return api_error("Each question needs a prompt, two choices and a valid answer.")
                cleaned.append({"prompt": str(question["prompt"]).strip()[:1000], "topic": str(question.get("topic", "")).strip()[:160], "options": options, "answer_index": answer, "explanation": str(question.get("explanation", ""))[:1000]})
            changes["questions"] = cleaned
        changes["updated_at"] = utcnow()
        try:
            result = quizzes.update_one({"_id": ObjectId(quiz_id)}, {"$set": changes})
        except Exception:
            result = None
        if not result or not result.matched_count:
            return api_error("Quiz not found.", 404)
        return jsonify({"quiz": serialize(quizzes.find_one({"_id": ObjectId(quiz_id)}))})

    @app.delete("/api/quizzes/<quiz_id>")
    @role_required("admin")
    def delete_quiz(quiz_id):
        try:
            result = quizzes.delete_one({"_id": ObjectId(quiz_id)})
        except Exception:
            result = None
        return (jsonify({"deleted": True}), 200) if result and result.deleted_count else api_error("Quiz not found.", 404)

    @app.post("/api/quizzes/<quiz_id>/submit")
    @role_required("student")
    def submit_quiz(quiz_id):
        try:
            quiz = quizzes.find_one({
                "_id": ObjectId(quiz_id),
                "published": True,
                "content_review_status": {"$ne": "review_revisions_needed"},
            })
        except Exception:
            quiz = None
        if not quiz:
            return api_error("Quiz not found.", 404)
        if not student_can_access_course(current_user(), quiz.get("course_id", "")):
            return api_error("Quiz not found.", 404)
        body = request.get_json(silent=True) or {}
        answers = body.get("answers")
        questions = quiz.get("questions", [])
        if not questions:
            return api_error("This quiz has no questions yet.", 409)
        if not isinstance(answers, list) or len(answers) != len(questions):
            return api_error("Submit one answer for each question.")
        if any(type(answer) is not int or answer < 0 or answer >= len(question.get("options", [])) for answer, question in zip(answers, questions)):
            return api_error("One or more answers are invalid.")
        correct = sum(1 for i, q in enumerate(questions) if answers[i] == q["answer_index"])
        total = len(questions)
        user = current_user()
        elapsed_seconds = body.get("elapsed_seconds", 0)
        if type(elapsed_seconds) is not int or elapsed_seconds < 0:
            elapsed_seconds = 0
        elapsed_seconds = min(elapsed_seconds, 86400)
        topic_breakdown = {}
        response_snapshot = []
        for i, question in enumerate(questions):
            topic_name = str(question.get("topic") or quiz.get("topic", "General"))
            is_correct = answers[i] == question["answer_index"]
            bucket = topic_breakdown.setdefault(topic_name, {"score": 0, "max_score": 0, "question_signatures": set()})
            bucket["score"] += int(is_correct)
            bucket["max_score"] += 1
            bucket["question_signatures"].add(question_signature(question.get("prompt")))
            response_snapshot.append({"prompt": question["prompt"], "topic": topic_name, "options": question["options"], "selected_index": answers[i], "is_correct": is_correct})
        topic_scores = [{"topic": name, "score": score["score"], "max_score": score["max_score"], "distinct_question_count": len(score["question_signatures"])} for name, score in topic_breakdown.items()]
        submitted_at = utcnow()
        attempt = {"student_id": user["_id"], "quiz_id": quiz["_id"], "quiz_title": quiz.get("title", "Practice quiz"), "course_id": quiz.get("course_id", ""), "topic": quiz.get("topic", "General"), "topic_scores": topic_scores, "score": correct, "max_score": total, "percentage": int(math.floor(100 * correct / total + 0.5)), "answers": answers, "responses": response_snapshot, "elapsed_seconds": elapsed_seconds, "created_at": submitted_at}
        result = attempts.insert_one(attempt)
        attempt["_id"] = result.inserted_id
        record_student_activity(user["_id"], "quiz_attempt")
        linked_outcomes = 0
        course_id = str(attempt.get("course_id", "")).upper()
        for topic_result in topic_scores:
            topic_name = topic_result["topic"]
            completed_session = study_session_completions.find_one(
                {"student_id": user["_id"], "course_id": course_id, "topic": topic_name,
                 "completed_at": {"$lte": submitted_at}, "follow_up_attempt_id": {"$exists": False}},
                sort=[("completed_at", -1)],
            )
            if not completed_session:
                continue
            percentage = int(math.floor(100 * topic_result["score"] / topic_result["max_score"] + 0.5)) if topic_result["max_score"] else 0
            baseline = completed_session.get("baseline_mastery")
            outcome = {
                "follow_up_attempt_id": result.inserted_id,
                "follow_up_at": submitted_at,
                "follow_up_score": topic_result["score"],
                "follow_up_max_score": topic_result["max_score"],
                "follow_up_unique_question_count": topic_result["distinct_question_count"],
                "follow_up_percentage": percentage,
            }
            baseline_questions = int(completed_session.get("baseline_question_count", 0))
            if isinstance(baseline, (int, float)) and baseline_questions >= MIN_DISTINCT_QUESTIONS_FOR_TOPIC_SIGNAL and topic_result["distinct_question_count"] >= MIN_DISTINCT_QUESTIONS_FOR_TOPIC_SIGNAL:
                outcome["score_change_points"] = percentage - baseline
            linked = study_session_completions.update_one(
                {"_id": completed_session["_id"], "follow_up_attempt_id": {"$exists": False}},
                {"$set": outcome},
            )
            linked_outcomes += linked.modified_count
        if course_id:
            course_completion_records.update_one(
                {"student_id": user["_id"], "course_id": course_id, "revision_due_at": {"$lte": submitted_at}, "revision_attempt_id": {"$exists": False}},
                {"$set": {"revision_attempt_id": result.inserted_id, "revision_attempted_at": submitted_at}},
            )
        return jsonify({"attempt": serialize(attempt), "learning_outcomes_linked": linked_outcomes, "review": [{"prompt": q["prompt"], "topic": q.get("topic", quiz.get("topic", "General")), "options": q["options"], "answer_index": q["answer_index"], "explanation": q.get("explanation", ""), "selected_index": answers[i], "correct": answers[i] == q["answer_index"], "review_status": q.get("review_status", "pending"), "reviewer_name": q.get("reviewer_name", ""), "reviewer_role": q.get("reviewer_role", ""), "source_url": q.get("source_url", ""), "review_date": q.get("review_date", "")} for i, q in enumerate(questions)]})

    @app.get("/api/progress")
    @role_required("student")
    def progress():
        user = current_user()
        recent = list(attempts.find({"student_id": user["_id"], "course_id": {"$in": student_track_course_ids(user)}}).sort("created_at", -1).limit(100))
        topic_scores = {}
        for item in recent:
            course_id = str(item.get("course_id", "")).upper()
            breakdown = item.get("topic_scores") or [{"topic": item.get("topic", "General"), "score": item.get("score", 0), "max_score": item.get("max_score", 0)}]
            for result in breakdown:
                group = topic_scores.setdefault((course_id, result.get("topic", "General")), {"attempts": 0, "score": 0, "max_score": 0, "question_signatures": set()})
                group["attempts"] += 1
                group["score"] += result.get("score", 0)
                group["max_score"] += result.get("max_score", 0)
            for response in item.get("responses", []):
                group = topic_scores.setdefault((course_id, response.get("topic", "General")), {"attempts": 0, "score": 0, "max_score": 0, "question_signatures": set()})
                signature = question_signature(response.get("prompt"))
                if signature:
                    group["question_signatures"].add(signature)
        topics = []
        for (course_id, name), values in topic_scores.items():
            unique_question_count = len(values["question_signatures"])
            topics.append({"course_id": course_id, "topic": name, "attempts": values["attempts"], "score": values["score"], "max_score": values["max_score"], "mastery": int(math.floor(100 * values["score"] / values["max_score"] + 0.5)) if values["max_score"] else 0, "distinct_question_count": unique_question_count, "evidence_status": "reliable" if unique_question_count >= MIN_DISTINCT_QUESTIONS_FOR_TOPIC_SIGNAL else "preliminary"})
        topics.sort(key=lambda item: (item["mastery"], item["topic"], item["course_id"]))

        # Keep the complete active-track topic catalog separate from assessed
        # signals so unattempted topics can be shown without treating them as
        # weak topics in recommendations or the study planner.
        track_courses = list(courses.find(
            {"course_id": {"$in": student_track_course_ids(user)}},
            {"course_id": 1, "title": 1, "subject": 1, "topics": 1, "topic_ids": 1},
        ).sort("title", ASCENDING))
        course_details = {
            str(item.get("course_id", "")).upper(): item for item in track_courses
        }
        track_course_ids = list(course_details)
        catalog_docs = list(topics_collection.find(
            {"course_id": {"$in": track_course_ids}},
            {"course_id": 1, "topic_id": 1, "topic_name": 1},
        ).sort([("course_id", ASCENDING), ("topic_id", ASCENDING)]))

        def topic_key(course_id, name):
            return (str(course_id or "").upper(), " ".join(str(name or "").casefold().split()))

        assessed_by_key = {topic_key(row["course_id"], row["topic"]): row for row in topics}
        catalog_topics = []
        matched_keys = set()
        catalog_keys = set()
        catalog_topic_ids = set()
        for topic in catalog_docs:
            course_id = str(topic.get("course_id", "")).upper()
            key = topic_key(course_id, topic.get("topic_name"))
            catalog_keys.add(key)
            if topic.get("topic_id"):
                catalog_topic_ids.add(str(topic["topic_id"]))
            assessed = assessed_by_key.get(key)
            if assessed:
                matched_keys.add(key)
            course = course_details.get(course_id, {})
            catalog_topics.append({
                "course_id": course_id,
                "course_title": course.get("title", course_id),
                "subject": course.get("subject", ""),
                "topic_id": topic.get("topic_id"),
                "topic": topic.get("topic_name", "Untitled topic"),
                "attempts": assessed["attempts"] if assessed else 0,
                "score": assessed["score"] if assessed else 0,
                "max_score": assessed["max_score"] if assessed else 0,
                "mastery": assessed["mastery"] if assessed else None,
                "distinct_question_count": assessed["distinct_question_count"] if assessed else 0,
                "evidence_status": assessed["evidence_status"] if assessed else "not_assessed",
                "in_catalog": True,
            })
        for course_id, course in course_details.items():
            for index, topic_name in enumerate(course.get("topics") or []):
                topic_ids = course.get("topic_ids") or []
                topic_id = topic_ids[index] if index < len(topic_ids) else None
                if topic_id and str(topic_id) in catalog_topic_ids:
                    continue
                key = topic_key(course_id, topic_name)
                if key in catalog_keys:
                    continue
                catalog_keys.add(key)
                assessed = assessed_by_key.get(key)
                if assessed:
                    matched_keys.add(key)
                catalog_topics.append({
                    "course_id": course_id,
                    "course_title": course.get("title", course_id),
                    "subject": course.get("subject", ""),
                    "topic_id": topic_id,
                    "topic": topic_name,
                    "attempts": assessed["attempts"] if assessed else 0,
                    "score": assessed["score"] if assessed else 0,
                    "max_score": assessed["max_score"] if assessed else 0,
                    "mastery": assessed["mastery"] if assessed else None,
                    "distinct_question_count": assessed["distinct_question_count"] if assessed else 0,
                    "evidence_status": assessed["evidence_status"] if assessed else "not_assessed",
                    "in_catalog": True,
                })
        for assessed in topics:
            key = topic_key(assessed["course_id"], assessed["topic"])
            if key in matched_keys:
                continue
            course = course_details.get(assessed["course_id"], {})
            catalog_topics.append({
                **assessed,
                "course_title": course.get("title", assessed["course_id"] or "Other quiz topics"),
                "subject": course.get("subject", ""),
                "topic_id": None,
                "in_catalog": False,
            })
        catalog_topics.sort(key=lambda item: (
            item["course_title"].casefold(), item["topic"].casefold(), item["course_id"]
        ))
        total = sum(x.get("max_score", 0) for x in recent)
        score = sum(x.get("score", 0) for x in recent)
        lesson_count = db.lesson_completions.count_documents({"student_id": user["_id"]})
        try:
            local_timezone = ZoneInfo(request.headers.get("X-Timezone", "UTC"))
        except Exception:
            local_timezone = timezone.utc
        activity_timestamps = [item.get("created_at") for item in recent if item.get("created_at")]
        activity_timestamps.extend(item.get("completed_at") for item in db.lesson_completions.find({"student_id": user["_id"]}, {"completed_at": 1}) if item.get("completed_at"))
        study_days = {(stamp.replace(tzinfo=timezone.utc) if stamp.tzinfo is None else stamp).astimezone(local_timezone).date() for stamp in activity_timestamps}
        streak = 0
        day = utcnow().astimezone(local_timezone).date()
        if day not in study_days and day - timedelta(days=1) in study_days:
            day -= timedelta(days=1)
        while day in study_days:
            streak += 1
            day -= timedelta(days=1)
        all_session_completions = study_session_completions.count_documents({"student_id": user["_id"]})
        outcome_summary = list(study_session_completions.aggregate([
            {"$match": {"student_id": user["_id"], "score_change_points": {"$type": "number"}, "baseline_question_count": {"$gte": MIN_DISTINCT_QUESTIONS_FOR_TOPIC_SIGNAL}, "follow_up_unique_question_count": {"$gte": MIN_DISTINCT_QUESTIONS_FOR_TOPIC_SIGNAL}}},
            {"$group": {"_id": None, "count": {"$sum": 1}, "average": {"$avg": "$score_change_points"}, "improved": {"$sum": {"$cond": [{"$gt": ["$score_change_points", 0]}, 1, 0]}}}},
        ]))
        outcome_summary = outcome_summary[0] if outcome_summary else {}
        current_plan = plans.find_one({"student_id": user["_id"]}) or {}
        current_plan_completed = study_session_completions.count_documents({"student_id": user["_id"], "plan_id": current_plan.get("plan_id")}) if current_plan.get("plan_id") else 0
        study_session_metrics = {
            "completed_all_time": all_session_completions,
            "completed_in_current_plan": current_plan_completed,
            "planned_in_current_plan": len(current_plan.get("tasks", [])),
            "follow_up_assessments": study_session_completions.count_documents({"student_id": user["_id"], "follow_up_attempt_id": {"$exists": True}}),
            "paired_assessments": outcome_summary.get("count", 0),
            "average_score_change_points": round(outcome_summary["average"], 1) if outcome_summary.get("count") else None,
            "improved_assessments": outcome_summary.get("improved", 0),
        }
        return jsonify({"summary": {"attempts": len(recent), "average": int(math.floor(100 * score / total + 0.5)) if total else 0, "completed_lessons": lesson_count, "streak_days": streak}, "study_sessions": study_session_metrics, "topics": topics, "topic_catalog": catalog_topics, "recent_attempts": serialize(recent[:12]), "score_trend_attempts": serialize(recent)})

    @app.post("/api/lessons/<lesson_id>/complete")
    @role_required("student")
    def complete_lesson(lesson_id):
        user = current_user()
        lesson = lessons.find_one({"_id": ObjectId(lesson_id), "published": True}) if ObjectId.is_valid(lesson_id) else None
        if not lesson or not student_can_access_course(user, lesson.get("course_id", "")):
            return api_error("Published lesson not found.", 404)
        db.lesson_completions.update_one(
            {"student_id": user["_id"], "lesson_id": lesson_id},
            {"$set": {"completed_at": utcnow()}}, upsert=True,
        )
        record_student_activity(user["_id"], "lesson_completion")
        return jsonify({"completed": True, "lesson_id": lesson_id})

    @app.get("/api/study-plan")
    @role_required("student")
    def get_study_plan():
        user = current_user()
        plan = plans.find_one({"student_id": user["_id"]})
        if plan and plan.get("learning_track") != normalize_student_profile(user.get("profile", {}))["program_track"]:
            plan = None
        if plan and plan.get("plan_id"):
            completion_rows = study_session_completions.find({"student_id": user["_id"], "plan_id": plan["plan_id"]})
            completed_by_id = {row["session_id"]: row for row in completion_rows}
            for task in plan.get("tasks", []):
                completion = completed_by_id.get(task.get("session_id"))
                task["completed"] = bool(completion)
                if completion:
                    task["completed_at"] = completion.get("completed_at")
                    task["follow_up_percentage"] = completion.get("follow_up_percentage")
                    task["follow_up_max_score"] = completion.get("follow_up_max_score")
                    task["follow_up_unique_question_count"] = completion.get("follow_up_unique_question_count")
                    task["score_change_points"] = completion.get("score_change_points")
                    task["follow_up_at"] = completion.get("follow_up_at")
        reminders = []
        for record in course_completion_records.find({"student_id": user["_id"], "revision_due_at": {"$lte": utcnow()}, "revision_attempt_id": {"$exists": False}}).sort("revision_due_at", ASCENDING):
            course = courses.find_one({"course_id": record["course_id"]}, {"title": 1, "subject": 1}) or {}
            reminders.append({"course_id": record["course_id"], "course_title": course.get("title", record["course_id"]), "subject": course.get("subject", "Course"), "completed_at": record.get("completed_at"), "revision_due_at": record.get("revision_due_at")})
        return jsonify({"plan": serialize(plan), "revision_reminders": serialize(reminders)})

    @app.post("/api/study-plan/sessions/<session_id>/complete")
    @role_required("student")
    def complete_study_session(session_id):
        user = current_user()
        plan = plans.find_one({"student_id": user["_id"], "tasks.session_id": session_id})
        if not plan or plan.get("learning_track") != normalize_student_profile(user.get("profile", {}))["program_track"]:
            return api_error("This session is not part of your current study plan.", 404)
        task = next((item for item in plan.get("tasks", []) if item.get("session_id") == session_id), None)
        if not task:
            return api_error("Study session not found.", 404)
        completed_at = utcnow()
        document = {
            "student_id": user["_id"], "plan_id": plan["plan_id"], "session_id": session_id,
            "course_id": str(task.get("course_id", "")).upper(), "topic": task.get("topic", ""),
            "reason_type": task.get("reason_type", "practice"), "reason": task.get("reason", ""),
            "scheduled_date": task.get("scheduled_date"), "minutes": task.get("minutes", 0),
            "baseline_mastery": task.get("baseline_mastery"),
            "baseline_question_count": task.get("baseline_question_count", 0), "completed_at": completed_at,
        }
        study_session_completions.update_one(
            {"student_id": user["_id"], "session_id": session_id},
            {"$setOnInsert": document}, upsert=True,
        )
        record_student_activity(user["_id"], "study_session_completion")
        completion = study_session_completions.find_one({"student_id": user["_id"], "session_id": session_id})
        return jsonify({"completed": True, "session": serialize(completion)})

    @app.get("/api/recommendations")
    @role_required("student")
    def recommendations():
        user = current_user()
        rows = list(attempts.find({"student_id": user["_id"], "course_id": {"$in": student_track_course_ids(user)}}).sort("created_at", -1).limit(100))
        by_topic = {}
        for row in rows:
            breakdown = row.get("topic_scores") or [{"topic": row.get("topic", "General"), "score": row.get("score", 0), "max_score": row.get("max_score", 0)}]
            for result in breakdown:
                key = (row.get("course_id", "").upper(), result.get("topic", "General"))
                stat = by_topic.setdefault(key, [0, 0, 0, set()])
                stat[0] += result.get("score", 0)
                stat[1] += result.get("max_score", 0)
                stat[2] += 1
            for response in row.get("responses", []):
                key = (row.get("course_id", "").upper(), response.get("topic", "General"))
                stat = by_topic.setdefault(key, [0, 0, 0, set()])
                signature = question_signature(response.get("prompt"))
                if signature:
                    stat[3].add(signature)
        student_history = []
        for row in reversed(rows):
            breakdown = row.get("topic_scores") or [{"topic": row.get("topic", "General"), "score": row.get("score", 0), "max_score": row.get("max_score", 0)}]
            for result in breakdown:
                maximum = result.get("max_score", 0)
                if not maximum:
                    continue
                course_id = str(row.get("course_id", "")).upper()
                topic_name = result.get("topic", "General")
                topic_doc = topics_collection.find_one({"course_id": course_id, "topic_name": topic_name}) if course_id else None
                student_history.append({"course_id": course_id, "topic_id": topic_doc.get("topic_id", "") if topic_doc else "", "score": 100 * result.get("score", 0) / maximum, "date": row.get("created_at")})
        model_predictions = []
        model_student_facing = bool(performance_model and performance_model.metrics.get("student_facing_eligible", False))
        if model_student_facing and by_topic:
            attempted_courses = sorted({course_id for course_id, _ in by_topic if course_id})
            for course_id in attempted_courses:
                for topic_doc in topics_collection.find({"course_id": course_id}):
                    prediction = performance_model.predict_score(student_history, course_id, topic_doc.get("topic_id"), topic_doc.get("difficulty_level"), utcnow())
                    model_predictions.append({"course_id": course_id, "topic_id": topic_doc.get("topic_id"), "topic": topic_doc.get("topic_name"), "predicted_next_score": prediction, "assessed": (course_id, topic_doc.get("topic_name")) in by_topic})
            model_predictions.sort(key=lambda item: item["predicted_next_score"])
        predicted_by_topic = {(item["course_id"], item["topic"]): item["predicted_next_score"] for item in model_predictions}
        guidance = []
        weak_by_course = {}
        for (course_id, topic_name), (score, maximum, count, question_signatures) in by_topic.items():
            if not maximum:
                continue
            mastery = round(100 * score / maximum)
            distinct_question_count = len(question_signatures)
            has_reliable_signal = distinct_question_count >= MIN_DISTINCT_QUESTIONS_FOR_TOPIC_SIGNAL
            status = ("Weak" if mastery < 50 else "Intermediate" if mastery < 80 else "Mastered") if has_reliable_signal else "Preliminary"
            topic_doc = topics_collection.find_one({"course_id": course_id, "topic_name": topic_name}) if course_id else None
            prereq_names = []
            if topic_doc:
                for edge in prerequisites.find({"topic_id": topic_doc["topic_id"]}):
                    prerequisite_topic = topics_collection.find_one({"topic_id": edge["prerequisite_topic_id"]})
                    if prerequisite_topic:
                        prereq_names.append({"topic": prerequisite_topic["topic_name"], "type": edge["prerequisite_type"]})
            if not has_reliable_signal:
                action = f"Answer at least {MIN_DISTINCT_QUESTIONS_FOR_TOPIC_SIGNAL} different questions on this topic before judging mastery."
            elif status == "Weak":
                action = "Revisit the foundations, then try a guided practice set."
            elif status == "Intermediate":
                action = "Practice this topic again, then retake a short quiz."
            else:
                action = "Try an applied project or move on to an advanced topic."
            guidance.append({"course_id": course_id, "topic": topic_name, "mastery": mastery, "question_responses": maximum, "distinct_question_count": distinct_question_count, "predicted_next_score": predicted_by_topic.get((course_id, topic_name)), "proficiency_status": status, "attempts": count, "next_step": action, "prerequisites": prereq_names})
            if has_reliable_signal and mastery < 80 and course_id:
                weak_by_course.setdefault(course_id, set()).add(topic_name)
        profile = normalize_student_profile(user.get("profile", {}))
        catalog = list(courses.find({"program_tracks": profile["program_track"]}))
        ranked = []
        for course in catalog:
            course_id = course.get("course_id", "").upper()
            actual_topics = sorted(weak_by_course.get(course_id, set()))
            reasons = []
            if actual_topics:
                reasons.append("Your quiz results show practice can strengthen " + ", ".join(actual_topics))
            if actual_topics:
                ranked.append({"course": course, "reason": ". ".join(reasons), "matched_topics": actual_topics})
        if not ranked:
            ranked = [{"course": course, "reason": "A good next course to explore", "matched_topics": []} for course in catalog[:4]]
        model_info = {
            "available": model_student_facing,
            "status": "validated" if model_student_facing else "experimental_not_shown",
            "message": None if model_student_facing else "Score forecasts are hidden until chronological holdout results beat the baseline by a meaningful margin.",
            "target": "next assessment score (0–100)",
            "metrics": performance_model.metrics if performance_model else None,
        }
        return jsonify({"recommendations": serialize(ranked[:6]), "topic_guidance": serialize(sorted(guidance, key=lambda x: (x["proficiency_status"] != "Preliminary", x["mastery"]))), "model_predictions": serialize(model_predictions[:30]), "model": model_info, "proficiency_bands": {"Weak": "0–49% with 3+ distinct questions", "Intermediate": "50–79% with 3+ distinct questions", "Mastered": "80–100% with 3+ distinct questions", "Preliminary": "Fewer than 3 distinct questions"}, "based_on_attempts": len(rows)})

    @app.post("/api/study-plan/generate")
    @role_required("student")
    def generate_plan():
        user = current_user()
        profile = normalize_student_profile(user.get("profile", {}))
        track_course_ids = student_track_course_ids(user)
        past = list(attempts.find({"student_id": user["_id"], "course_id": {"$in": track_course_ids}}).sort("created_at", -1).limit(100))
        topic_scores = {}
        for item in past:
            course_id = item.get("course_id", "").upper()
            breakdown = item.get("topic_scores") or [{"topic": item.get("topic", "General"), "score": item.get("score", 0), "max_score": item.get("max_score", 0)}]
            for result in breakdown:
                row = topic_scores.setdefault((course_id, result.get("topic", "General")), {"score": 0, "total": 0, "assessments": 0, "question_signatures": set()})
                row["score"] += result.get("score", 0)
                row["total"] += result.get("max_score", 0)
                row["assessments"] += 1
            for response in item.get("responses", []):
                row = topic_scores.setdefault((course_id, response.get("topic", "General")), {"score": 0, "total": 0, "assessments": 0, "question_signatures": set()})
                signature = question_signature(response.get("prompt"))
                if signature:
                    row["question_signatures"].add(signature)
        ranked = sorted(topic_scores.items(), key=lambda pair: pair[1]["score"] / pair[1]["total"] if pair[1]["total"] else 0)
        # One or two answers are too little evidence to label a topic weak.
        # Keep those topics eligible for a first-check plan, but only use a
        # weak-score recommendation once the student has answered at least
        # three distinct questions tagged to that topic.
        needs_practice = [
            (key, value) for key, value in ranked
            if len(value["question_signatures"]) >= MIN_DISTINCT_QUESTIONS_FOR_TOPIC_SIGNAL
            and value["score"] / value["total"] < 0.8
        ]
        course_rows = list(courses.find({"program_tracks": profile["program_track"]}))
        active_course_ids = {course["course_id"] for course in course_rows}
        enrolled_ids = {row["course_id"] for row in enrollments.find({"student_id": user["_id"]})}
        course_rows.sort(key=lambda course: (course.get("course_id") not in enrolled_ids, course.get("title", "")))
        # Keep an adaptive plan grounded in the student's chosen learning path.
        # If there are weak topics in enrolled courses, don't pad the plan with
        # unrelated catalog courses. Otherwise use courses they have attempted.
        attempted_course_ids = {course_id for course_id, _topic in topic_scores if course_id in active_course_ids}
        needs_practice = [pair for pair in needs_practice if pair[0][0] in active_course_ids]
        enrolled_weak = [pair for pair in needs_practice if pair[0][0] in enrolled_ids]
        attempted_weak = [pair for pair in needs_practice if pair[0][0] in attempted_course_ids]
        if enrolled_weak:
            needs_practice = enrolled_weak
        elif attempted_weak:
            needs_practice = attempted_weak
        goal_mode = profile["goal_mode"]
        planned_topics = []
        seen_topics = set()

        def add_topic(course_id, topic_name, activity, reason_type, reason, baseline_mastery=None):
            key = (course_id, topic_name)
            if topic_name and key not in seen_topics:
                if baseline_mastery is None:
                    baseline_stats = topic_scores.get(key)
                    if baseline_stats and len(baseline_stats.get("question_signatures", set())) >= MIN_DISTINCT_QUESTIONS_FOR_TOPIC_SIGNAL:
                        baseline_mastery = int(math.floor(100 * baseline_stats["score"] / baseline_stats["total"] + 0.5))
                baseline_stats = topic_scores.get(key)
                planned_topics.append({
                    "course_id": course_id, "topic": topic_name, "activity": activity,
                    "reason_type": reason_type, "reason": reason,
                    "baseline_mastery": baseline_mastery,
                    "baseline_question_count": len(baseline_stats.get("question_signatures", set())) if baseline_stats else 0,
                })
                seen_topics.add(key)

        if goal_mode == "explore_courses":
            explore_rows = [course for course in course_rows if course.get("course_id") in enrolled_ids] or course_rows
            for course in explore_rows:
                course_id = str(course.get("course_id", "")).upper()
                course_topics = course.get("topics") or []
                if course_topics:
                    add_topic(course_id, course_topics[0], "Explore a course lesson, then try its practice quiz", "explore", "A starter topic from a course in your current learning path.")
                if len(planned_topics) >= 3:
                    break
        else:
            needs_practice = needs_practice[:3]
            for (course_id, topic), _stats in needs_practice:
                topic_doc = topics_collection.find_one({"course_id": course_id, "topic_name": topic}) if course_id else None
                if topic_doc and goal_mode == "foundations":
                    # Walk the full prerequisite chain so foundational topics come first.
                    pending = [topic_doc["topic_id"]]
                    visited = set()
                    ancestors = []
                    while pending:
                        current_id = pending.pop(0)
                        if current_id in visited:
                            continue
                        visited.add(current_id)
                        edges = list(prerequisites.find({"topic_id": current_id}))
                        for edge in edges:
                            prereq_id = edge.get("prerequisite_topic_id")
                            prereq_doc = topics_collection.find_one({"topic_id": prereq_id}) if prereq_id else None
                            if prereq_doc:
                                pending.append(prereq_id)
                                if prereq_id != topic_doc["topic_id"]:
                                    ancestors.append(prereq_doc)
                    # Add deeper prerequisites before their dependent topics.
                    for prerequisite_doc in reversed(ancestors):
                        add_topic(course_id, prerequisite_doc["topic_name"], "Review this prerequisite before moving to the next concept", "prerequisite", f"This is a listed prerequisite for {topic}.", None)
                elif topic_doc:
                    for edge in prerequisites.find({"topic_id": topic_doc["topic_id"]}):
                        prereq_doc = topics_collection.find_one({"topic_id": edge.get("prerequisite_topic_id")})
                        if prereq_doc:
                            add_topic(course_id, prereq_doc["topic_name"], "Review a prerequisite foundation before the next quiz", "prerequisite", f"This is a listed prerequisite for {topic}.", None)
                stats = _stats
                mastery = int(math.floor(100 * stats["score"] / stats["total"] + 0.5)) if stats.get("total") else None
                assessment_count = stats.get("assessments", 0)
                unique_question_count = len(stats.get("question_signatures", set()))
                if unique_question_count >= MIN_DISTINCT_QUESTIONS_FOR_TOPIC_SIGNAL and mastery is not None:
                    reason = f"Your quiz mastery is {mastery}% across {assessment_count} recent assessment{'s' if assessment_count != 1 else ''}."
                    reason_type = "weak_score"
                elif unique_question_count:
                    reason = f"This is a preliminary signal from {unique_question_count} distinct question{'s' if unique_question_count != 1 else ''}; collect at least {MIN_DISTINCT_QUESTIONS_FOR_TOPIC_SIGNAL} before Nebula treats it as a weak topic."
                    reason_type = "practice"
                else:
                    reason = "This topic is in your learning path and is ready for a first check."
                    reason_type = "practice"
                reliable_baseline = mastery if unique_question_count >= MIN_DISTINCT_QUESTIONS_FOR_TOPIC_SIGNAL else None
                add_topic(course_id, topic, "Review the lesson, then try a focused practice quiz", reason_type, reason, reliable_baseline)

        try:
            local_timezone = ZoneInfo(request.headers.get("X-Timezone", "UTC"))
        except Exception:
            local_timezone = timezone.utc
        today = datetime.now(local_timezone).date()

        # Bring topics back for spaced review after a completed session has a
        # follow-up quiz. Shorter intervals are used when the check is weaker.
        review_history = study_session_completions.find(
            {"student_id": user["_id"], "follow_up_at": {"$exists": True}}
        ).sort("follow_up_at", -1).limit(200)
        latest_review_keys = set()
        spaced_review_topics = []
        for reviewed in review_history:
            review_key = (reviewed.get("course_id", ""), reviewed.get("topic", ""))
            if not review_key[0] or not review_key[1] or review_key in latest_review_keys:
                continue
            latest_review_keys.add(review_key)
            if review_key[0] not in active_course_ids:
                continue
            score_pct = reviewed.get("follow_up_percentage")
            if not isinstance(score_pct, (int, float)) or reviewed.get("follow_up_unique_question_count", 0) < MIN_DISTINCT_QUESTIONS_FOR_TOPIC_SIGNAL:
                continue
            interval_days = 1 if score_pct < 50 else 3 if score_pct < 80 else 7
            follow_up_at = reviewed["follow_up_at"]
            if follow_up_at.tzinfo is None:
                follow_up_at = follow_up_at.replace(tzinfo=timezone.utc)
            due_at = follow_up_at + timedelta(days=interval_days)
            if due_at.astimezone(local_timezone).date() <= today:
                baseline_stats = topic_scores.get(review_key)
                baseline = int(math.floor(100 * baseline_stats["score"] / baseline_stats["total"] + 0.5)) if baseline_stats and baseline_stats["total"] else None
                already_planned = review_key in seen_topics
                add_topic(
                    review_key[0], review_key[1], "Revisit this concept, then check what you still remember",
                    "spaced_review",
                    f"Spaced review is due: your last check was {score_pct}% on {follow_up_at.astimezone(local_timezone).strftime('%b %d')}.",
                    baseline,
                )
                if not already_planned:
                    spaced_review_topics.append(planned_topics[-1])

        if not planned_topics:
            starter_courses = [course for course in course_rows if not enrolled_ids or course.get("course_id") in enrolled_ids][:3]
            for course in starter_courses:
                course_id = str(course.get("course_id", "")).upper()
                add_topic(course_id, (course.get("topics") or ["Explore your next topic"])[0], "Study a lesson and complete a practice quiz", "starter", "A starting point while Nebula learns which topics you already know.")

        if len(planned_topics) > 7:
            non_review_topics = [item for item in planned_topics if item.get("reason_type") != "spaced_review"]
            planned_topics = non_review_topics[:max(0, 7 - min(2, len(spaced_review_topics)))] + spaced_review_topics[:2]

        # Schedule sessions only on selected weekdays and cap each session at the
        # student's preferred length (or their smaller daily time budget).
        day_minutes = profile["daily_minutes"]
        session_minutes = min(profile["preferred_session_minutes"], day_minutes)
        sessions_per_day = max(1, math.ceil(day_minutes / session_minutes))
        allowed_weekdays = {STUDY_DAYS.index(day) for day in profile["available_days"]}
        cursor = today
        daily_counts = {}
        tasks = []
        plan_id = secrets.token_urlsafe(18)
        for item in planned_topics[:7]:
            while cursor.weekday() not in allowed_weekdays or daily_counts.get(cursor, 0) >= sessions_per_day:
                cursor += timedelta(days=1)
            used_sessions = daily_counts.get(cursor, 0)
            task_minutes = min(session_minutes, day_minutes - used_sessions * session_minutes)
            daily_counts[cursor] = used_sessions + 1
            day_label = "TODAY" if cursor == today else f"{cursor.strftime('%a').upper()} · {cursor.strftime('%b')} {cursor.day}"
            tasks.append({**item, "session_id": secrets.token_urlsafe(18), "day": len(tasks) + 1, "day_label": day_label, "scheduled_date": cursor.isoformat(), "minutes": task_minutes})
        plan = {
            "student_id": user["_id"], "plan_id": plan_id, "learning_track": profile["learning_track"],
            "learning_track_label": CURRICULUM_TRACKS[profile["program_track"]].get("display_name", profile["program_track"]), "goal": profile["goal"], "goal_mode": goal_mode,
            "daily_minutes": day_minutes, "available_days": profile["available_days"],
            "preferred_session_minutes": profile["preferred_session_minutes"], "session_minutes": session_minutes,
            "tasks": tasks, "generated_at": utcnow(),
        }
        plans.update_one({"student_id": user["_id"]}, {"$set": plan}, upsert=True)
        return jsonify({"plan": serialize(plan)})

    @app.get("/api/admin/overview")
    @role_required("admin")
    def admin_overview():
        today = utcnow().date()
        tracking_start = pilot_tracking_started_at
        if tracking_start.tzinfo is None:
            tracking_start = tracking_start.replace(tzinfo=timezone.utc)
        pilot_students = list(users.find(
            {"role": "student", "created_at": {"$gte": tracking_start}},
            {"_id": 1, "created_at": 1},
        ))
        student_ids = [student["_id"] for student in pilot_students]
        target_days = {}
        eligible_day1 = []
        eligible_day7 = []
        for student in pilot_students:
            created_at = student.get("created_at")
            if not created_at:
                continue
            if created_at.tzinfo is None:
                created_at = created_at.replace(tzinfo=timezone.utc)
            signup_day = created_at.astimezone(timezone.utc).date()
            day1 = signup_day + timedelta(days=1)
            day7 = signup_day + timedelta(days=7)
            target_days[(student["_id"], "d1")] = day1.isoformat()
            target_days[(student["_id"], "d7")] = day7.isoformat()
            if day1 <= today:
                eligible_day1.append(student["_id"])
            if day7 <= today:
                eligible_day7.append(student["_id"])
        target_date_values = list(set(target_days.values()))
        active_pairs = set()
        if student_ids and target_date_values:
            for activity in student_activity_days.find(
                {"student_id": {"$in": student_ids}, "activity_date": {"$in": target_date_values}},
                {"student_id": 1, "activity_date": 1},
            ):
                active_pairs.add((activity["student_id"], activity["activity_date"]))

        def retention_metric(day_key, eligible):
            returned = sum(1 for student_id in eligible if (student_id, target_days[(student_id, day_key)]) in active_pairs)
            count = len(eligible)
            return {"returned": returned, "eligible": count, "percent": round(100 * returned / count, 1) if count else None}

        current_plans = list(plans.find({}, {"student_id": 1, "plan_id": 1, "tasks": 1}))
        plan_ids = [plan.get("plan_id") for plan in current_plans if plan.get("plan_id")]
        planned_sessions = sum(len(plan.get("tasks", [])) for plan in current_plans)
        completed_sessions = study_session_completions.count_documents({"plan_id": {"$in": plan_ids}}) if plan_ids else 0
        paired_outcomes = list(study_session_completions.aggregate([
            {"$match": {"score_change_points": {"$type": "number"}, "baseline_question_count": {"$gte": MIN_DISTINCT_QUESTIONS_FOR_TOPIC_SIGNAL}, "follow_up_unique_question_count": {"$gte": MIN_DISTINCT_QUESTIONS_FOR_TOPIC_SIGNAL}}},
            {"$group": {"_id": None, "count": {"$sum": 1}, "average": {"$avg": "$score_change_points"}, "improved": {"$sum": {"$cond": [{"$gt": ["$score_change_points", 0]}, 1, 0]}}}},
        ]))
        paired_outcomes = paired_outcomes[0] if paired_outcomes else {}
        learning_pairs = study_session_completions.count_documents({"follow_up_attempt_id": {"$exists": True}})
        tracking_day = tracking_start.astimezone(timezone.utc).date().isoformat()
        pilot = {
            "tracking_started_at": tracking_start,
            "retention": {"d1": retention_metric("d1", eligible_day1), "d7": retention_metric("d7", eligible_day7), "cohort_tracking_since": tracking_day},
            "current_plans": {"students": len(current_plans), "planned_sessions": planned_sessions, "completed_sessions": completed_sessions, "completion_percent": round(100 * completed_sessions / planned_sessions, 1) if planned_sessions else None},
            "learning_checks": {"follow_up_pairs": learning_pairs, "eligible_score_pairs": paired_outcomes.get("count", 0), "average_score_change_points": round(paired_outcomes["average"], 1) if paired_outcomes.get("count") else None, "improved_pairs": paired_outcomes.get("improved", 0)},
            "definitions": {"retention": "Student had an authenticated app visit or learning activity on the exact UTC day 1 or day 7 after signup.", "completion": "Completed sessions divided by sessions in each student's latest saved plan.", "score_change": "Descriptive topic score difference; at least three distinct questions required in both baseline and follow-up."},
        }
        return jsonify({"students": users.count_documents({"role": "student"}), "admins": users.count_documents({"role": "admin"}), "courses": courses.count_documents({}), "quizzes": quizzes.count_documents({}), "published_quizzes": quizzes.count_documents({"published": True}), "attempts": attempts.count_documents({}), "pilot": serialize(pilot)})

    @app.errorhandler(400)
    def bad_request(_error):
        return api_error("The request could not be understood.", 400)

    @app.errorhandler(404)
    def not_found(_error):
        return api_error("The requested endpoint was not found.", 404)

    return app


app = None if os.getenv("NEBULA_SKIP_DEFAULT_APP", "false").lower() == "true" else create_app()

if __name__ == "__main__":
    app = app or create_app()
    app.run(host="127.0.0.1", port=int(os.getenv("PORT", "5000")), debug=os.getenv("FLASK_DEBUG", "false").lower() == "true")
