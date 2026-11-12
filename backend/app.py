"""Nebula API: authentication, learning activity, recommendations, and admin tools."""
from __future__ import annotations

import os
import re
import json
import math
import secrets
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
            elif (existing_quiz.get("title") == starter_quiz["title"]
                  and len(existing_quiz.get("questions", [])) < len(starter_quiz["questions"])):
                # Upgrade older Nebula-generated starter diagnostics without touching admin quizzes.
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

    def current_user():
        identity = get_jwt_identity()
        try:
            user = users.find_one({"_id": ObjectId(identity)})
        except Exception:
            user = None
        return user

    def user_is_active(user):
        # Accounts created before status management are active by default.
        return user is not None and user.get("status", "active") == "active"

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
            if app.config["NEBULA_ENV"] != "production":
                # In local development, read the project's .env at request time
                # so edits take effect even if a stale Flask process is running.
                expected_key = dotenv_values(ENV_FILE).get("ADMIN_SIGNUP_KEY") or expected_key
            if not expected_key or supplied_key != expected_key:
                return api_error("Admin registration requires a valid setup key.", 403)
        profile = body.get("profile", {}) if isinstance(body.get("profile", {}), dict) else {}
        try:
            daily_minutes = max(10, min(480, int(profile.get("daily_minutes", 60) or 60)))
        except (TypeError, ValueError):
            return api_error("Study time must be a whole number of minutes from 10 to 480.")
        user = {
            "name": name,
            "email": email,
            "password_hash": generate_password_hash(password),
            "role": role,
            "status": "active",
            "profile": {
                "goal": str(profile.get("goal", ""))[:160],
                "level": str(profile.get("level", ""))[:80],
                "daily_minutes": daily_minutes,
            } if role == "student" else {},
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
        return jsonify({"access_token": token, "user": serialize(user)})

    @app.get("/api/auth/me")
    @jwt_required()
    def me():
        user = current_user()
        if not user or not user_is_active(user):
            return api_error("Account not found.", 404)
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
            daily_minutes = max(10, min(480, int(profile.get("daily_minutes", user.get("profile", {}).get("daily_minutes", 60)))))
        except (TypeError, ValueError):
            return api_error("Study time must be a whole number of minutes from 10 to 480.")
        updated = {
            "goal": str(profile.get("goal", user.get("profile", {}).get("goal", "")))[:160],
            "level": str(profile.get("level", user.get("profile", {}).get("level", "")))[:80],
            "daily_minutes": daily_minutes,
        }
        users.update_one({"_id": user["_id"]}, {"$set": {"profile": updated}})
        user["profile"] = updated
        return jsonify({"user": serialize(user)})

    @app.get("/api/courses")
    @jwt_required()
    def list_courses():
        if not user_is_active(current_user()):
            return api_error("This account is suspended.", 403)
        cursor = courses.find({}).sort("title", ASCENDING)
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
        if not courses.find_one({"course_id": course_id}):
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
        if not user_is_active(current_user()):
            return api_error("This account is suspended.", 403)
        course_id = course_id.upper()
        if not courses.find_one({"course_id": course_id}):
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

    @app.get("/api/courses/<course_id>/lessons")
    @jwt_required()
    def list_course_lessons(course_id):
        user = current_user()
        if not user_is_active(user):
            return api_error("This account is suspended.", 403)
        course_id = course_id.upper()
        if not courses.find_one({"course_id": course_id}):
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
        allowed = {"title", "subject", "level", "description", "estimated_hours", "topics"}
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
        query = {"published": True} if is_student else {}
        items = list(quizzes.find(query).sort("title", ASCENDING))
        if is_student:
            for quiz in items:
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
        if not quiz or (user.get("role") == "student" and not quiz.get("published")):
            return api_error("Quiz not found.", 404)
        if user.get("role") == "student":
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
        doc = {"title": title[:120], "course_id": str(body.get("course_id", ""))[:40], "topic": str(body.get("topic", "General"))[:100], "difficulty": str(body.get("difficulty", "medium")), "questions": cleaned, "published": bool(body.get("published", False)), "created_at": utcnow()}
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
            quiz = quizzes.find_one({"_id": ObjectId(quiz_id), "published": True})
        except Exception:
            quiz = None
        if not quiz:
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
            bucket = topic_breakdown.setdefault(topic_name, {"score": 0, "max_score": 0})
            bucket["score"] += int(is_correct)
            bucket["max_score"] += 1
            response_snapshot.append({"prompt": question["prompt"], "topic": topic_name, "options": question["options"], "selected_index": answers[i], "is_correct": is_correct})
        topic_scores = [{"topic": name, **score} for name, score in topic_breakdown.items()]
        attempt = {"student_id": user["_id"], "quiz_id": quiz["_id"], "quiz_title": quiz.get("title", "Practice quiz"), "course_id": quiz.get("course_id", ""), "topic": quiz.get("topic", "General"), "topic_scores": topic_scores, "score": correct, "max_score": total, "percentage": int(math.floor(100 * correct / total + 0.5)), "answers": answers, "responses": response_snapshot, "elapsed_seconds": elapsed_seconds, "created_at": utcnow()}
        result = attempts.insert_one(attempt)
        attempt["_id"] = result.inserted_id
        return jsonify({"attempt": serialize(attempt), "review": [{"prompt": q["prompt"], "topic": q.get("topic", quiz.get("topic", "General")), "options": q["options"], "answer_index": q["answer_index"], "explanation": q.get("explanation", ""), "selected_index": answers[i], "correct": answers[i] == q["answer_index"]} for i, q in enumerate(questions)]})

    @app.get("/api/progress")
    @role_required("student")
    def progress():
        user = current_user()
        recent = list(attempts.find({"student_id": user["_id"]}).sort("created_at", -1).limit(100))
        topic_scores = {}
        for item in recent:
            course_id = str(item.get("course_id", "")).upper()
            breakdown = item.get("topic_scores") or [{"topic": item.get("topic", "General"), "score": item.get("score", 0), "max_score": item.get("max_score", 0)}]
            for result in breakdown:
                group = topic_scores.setdefault((course_id, result.get("topic", "General")), {"attempts": 0, "score": 0, "max_score": 0})
                group["attempts"] += 1
                group["score"] += result.get("score", 0)
                group["max_score"] += result.get("max_score", 0)
        topics = [{"course_id": course_id, "topic": name, **values, "mastery": int(math.floor(100 * values["score"] / values["max_score"] + 0.5)) if values["max_score"] else 0} for (course_id, name), values in topic_scores.items()]
        topics.sort(key=lambda item: (item["mastery"], item["topic"], item["course_id"]))
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
        return jsonify({"summary": {"attempts": len(recent), "average": int(math.floor(100 * score / total + 0.5)) if total else 0, "completed_lessons": lesson_count, "streak_days": streak}, "topics": topics, "recent_attempts": serialize(recent[:12]), "score_trend_attempts": serialize(recent)})

    @app.post("/api/lessons/<lesson_id>/complete")
    @role_required("student")
    def complete_lesson(lesson_id):
        user = current_user()
        lesson = lessons.find_one({"_id": ObjectId(lesson_id), "published": True}) if ObjectId.is_valid(lesson_id) else None
        if not lesson:
            return api_error("Published lesson not found.", 404)
        db.lesson_completions.update_one(
            {"student_id": user["_id"], "lesson_id": lesson_id},
            {"$set": {"completed_at": utcnow()}}, upsert=True,
        )
        return jsonify({"completed": True, "lesson_id": lesson_id})

    @app.get("/api/study-plan")
    @role_required("student")
    def get_study_plan():
        plan = plans.find_one({"student_id": current_user()["_id"]})
        return jsonify({"plan": serialize(plan)})

    @app.get("/api/recommendations")
    @role_required("student")
    def recommendations():
        user = current_user()
        rows = list(attempts.find({"student_id": user["_id"]}).sort("created_at", -1).limit(100))
        by_topic = {}
        for row in rows:
            breakdown = row.get("topic_scores") or [{"topic": row.get("topic", "General"), "score": row.get("score", 0), "max_score": row.get("max_score", 0)}]
            for result in breakdown:
                key = (row.get("course_id", "").upper(), result.get("topic", "General"))
                stat = by_topic.setdefault(key, [0, 0, 0])
                stat[0] += result.get("score", 0)
                stat[1] += result.get("max_score", 0)
                stat[2] += 1
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
        for (course_id, topic_name), (score, maximum, count) in by_topic.items():
            if not maximum:
                continue
            mastery = round(100 * score / maximum)
            status = "Weak" if mastery < 50 else "Intermediate" if mastery < 80 else "Mastered"
            topic_doc = topics_collection.find_one({"course_id": course_id, "topic_name": topic_name}) if course_id else None
            prereq_names = []
            if topic_doc:
                for edge in prerequisites.find({"topic_id": topic_doc["topic_id"]}):
                    prerequisite_topic = topics_collection.find_one({"topic_id": edge["prerequisite_topic_id"]})
                    if prerequisite_topic:
                        prereq_names.append({"topic": prerequisite_topic["topic_name"], "type": edge["prerequisite_type"]})
            if status == "Weak":
                action = "Revisit the foundations, then try a guided practice set."
            elif status == "Intermediate":
                action = "Practice this topic again, then retake a short quiz."
            else:
                action = "Try an applied project or move on to an advanced topic."
            guidance.append({"course_id": course_id, "topic": topic_name, "mastery": mastery, "predicted_next_score": predicted_by_topic.get((course_id, topic_name)), "proficiency_status": status, "attempts": count, "next_step": action, "prerequisites": prereq_names})
            if mastery < 80 and course_id:
                weak_by_course.setdefault(course_id, set()).add(topic_name)
        catalog = list(courses.find({}))
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
        return jsonify({"recommendations": serialize(ranked[:6]), "topic_guidance": serialize(sorted(guidance, key=lambda x: x["mastery"])), "model_predictions": serialize(model_predictions[:30]), "model": model_info, "proficiency_bands": {"Weak": "0–49%", "Intermediate": "50–79%", "Mastered": "80–100%"}, "based_on_attempts": len(rows)})

    @app.post("/api/study-plan/generate")
    @role_required("student")
    def generate_plan():
        user = current_user()
        past = list(attempts.find({"student_id": user["_id"]}).sort("created_at", -1).limit(100))
        topic_scores = {}
        for item in past:
            course_id = item.get("course_id", "").upper()
            breakdown = item.get("topic_scores") or [{"topic": item.get("topic", "General"), "score": item.get("score", 0), "max_score": item.get("max_score", 0)}]
            for result in breakdown:
                row = topic_scores.setdefault((course_id, result.get("topic", "General")), {"score": 0, "total": 0})
                row["score"] += result.get("score", 0)
                row["total"] += result.get("max_score", 0)
        ranked = sorted(topic_scores.items(), key=lambda pair: pair[1]["score"] / pair[1]["total"] if pair[1]["total"] else 0)
        needs_practice = [(key, value) for key, value in ranked if value["total"] and value["score"] / value["total"] < 0.8]
        available = courses.find({})
        course_rows = list(available)
        enrolled_ids = {row["course_id"] for row in enrollments.find({"student_id": user["_id"]})}
        course_rows.sort(key=lambda course: (course.get("course_id") not in enrolled_ids, course.get("title", "")))
        needs_practice.sort(key=lambda pair: (pair[0][0] not in enrolled_ids, pair[1]["score"] / pair[1]["total"] if pair[1]["total"] else 0))
        needs_practice = needs_practice[:3]
        day_minutes = user.get("profile", {}).get("daily_minutes", 60)
        tasks = []
        for (course_id, topic), stats in needs_practice:
            course = next((c for c in course_rows if c.get("course_id", "").upper() == course_id), None)
            topic_doc = topics_collection.find_one({"course_id": course_id, "topic_name": topic}) if course_id else None
            prerequisite_rows = list(prerequisites.find({"topic_id": topic_doc["topic_id"]})) if topic_doc else []
            already_planned = {task["topic"] for task in tasks}
            for edge in prerequisite_rows:
                prereq_doc = topics_collection.find_one({"topic_id": edge["prerequisite_topic_id"]})
                if prereq_doc and prereq_doc["topic_name"] not in already_planned:
                    tasks.append({"day": len(tasks) + 1, "topic": prereq_doc["topic_name"], "course_id": course_id, "minutes": max(5, day_minutes // 3), "activity": "Review a prerequisite foundation before the next quiz"})
                    already_planned.add(prereq_doc["topic_name"])
            tasks.append({"day": len(tasks) + 1, "topic": topic, "course_id": course.get("course_id") if course else None, "minutes": max(5, day_minutes // 2), "activity": "Review the lesson, then try a focused practice quiz"})
        if not tasks:
            starter_courses = [course for course in course_rows if not enrolled_ids or course.get("course_id") in enrolled_ids][:3]
            tasks = [{"day": i + 1, "topic": (c.get("topics") or ["Explore your next topic"])[0], "course_id": c.get("course_id"), "minutes": max(5, day_minutes // 2), "activity": "Study a lesson and complete a practice quiz"} for i, c in enumerate(starter_courses)]
        tasks = tasks[:7]
        for index, task in enumerate(tasks):
            task["day"] = index + 1
            task["day_label"] = "TODAY" if index == 0 else f"DAY {index + 1}"
        plan = {"student_id": user["_id"], "goal": user.get("profile", {}).get("goal", "Build a steady study habit"), "daily_minutes": day_minutes, "tasks": tasks, "generated_at": utcnow()}
        plans.update_one({"student_id": user["_id"]}, {"$set": plan}, upsert=True)
        return jsonify({"plan": serialize(plan)})

    @app.get("/api/admin/overview")
    @role_required("admin")
    def admin_overview():
        return jsonify({"students": users.count_documents({"role": "student"}), "admins": users.count_documents({"role": "admin"}), "courses": courses.count_documents({}), "quizzes": quizzes.count_documents({}), "attempts": attempts.count_documents({})})

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
