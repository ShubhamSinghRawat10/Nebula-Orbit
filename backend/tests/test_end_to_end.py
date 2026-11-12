"""Isolated API acceptance checks for Nebula's student and admin journeys."""
from __future__ import annotations

import os
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

import mongomock

BACKEND = Path(__file__).resolve().parents[1]
os.environ["NEBULA_SKIP_DEFAULT_APP"] = "true"
sys.path.insert(0, str(BACKEND))
from app import create_app  # noqa: E402
from data_loader import import_curriculum  # noqa: E402
os.environ.pop("NEBULA_SKIP_DEFAULT_APP", None)


def auth(token):
    return {"Authorization": f"Bearer {token}"}


def register(client, *, role="student", email="student@example.test", **extra):
    return client.post("/api/auth/register", json={
        "name": "Nebula Learner", "email": email,
        "password": "Long-test-password-2026", "role": role,
        "profile": {"goal": "Pass my CS exams", "level": "Year 1", "daily_minutes": 45},
        **extra,
    })


class NebulaAcceptanceTests(unittest.TestCase):
    def setUp(self):
        self.mongo = mongomock.MongoClient()
        self.application = create_app({
            "TESTING": True, "MONGODB_CLIENT": self.mongo,
            "MONGODB_DB": "nebula_acceptance",
            "JWT_SECRET_KEY": "isolated-acceptance-secret-long-enough-2026",
            "ADMIN_SIGNUP_KEY": "isolated-admin-invitation-2026",
            "FRONTEND_ORIGIN": "http://localhost:5173",
        })
        self.client = self.application.test_client()
        self.db = self.mongo["nebula_acceptance"]
        self.db.courses.insert_one({
            "course_id": "DSA", "title": "Data Structures & Algorithms",
            "subject": "Computer Science", "level": "Beginner",
            "description": "Core data structures and algorithms.",
            "estimated_hours": 30, "topics": ["Foundations", "Algorithm analysis"],
            "topic_ids": ["DSA_T1", "DSA_T2"],
        })
        self.db.topics.insert_many([
            {"topic_id": "DSA_T1", "course_id": "DSA", "topic_name": "DSA - Foundations", "difficulty_level": "Beginner"},
            {"topic_id": "DSA_T2", "course_id": "DSA", "topic_name": "DSA - Algorithm analysis", "difficulty_level": "Beginner"},
        ])
        self.db.prerequisites.insert_one({
            "edge_id": "DSA_T2-DSA_T1", "topic_id": "DSA_T2",
            "prerequisite_topic_id": "DSA_T1", "prerequisite_type": "Direct",
        })
        self.db.quizzes.insert_one({
            "title": "DSA foundations diagnostic", "course_id": "DSA",
            "topic": "DSA - Algorithm analysis", "difficulty": "mixed",
            "published": True, "created_at": datetime.now(timezone.utc),
            "questions": [{
                "prompt": f"Question {index + 1}: select the correct answer.",
                "topic": "DSA - Algorithm analysis",
                "options": ["Incorrect", "Correct", "Not this one", "Also incorrect"],
                "answer_index": 1, "explanation": "The second option is correct.",
            } for index in range(8)],
        })

    def tearDown(self):
        self.mongo.close()

    def test_student_quiz_score_progress_plan_recommendation_and_restart(self):
        signup = register(self.client)
        self.assertEqual(signup.status_code, 201)
        headers = auth(signup.json["access_token"])
        quiz_list = self.client.get("/api/quizzes", headers=headers)
        self.assertEqual(quiz_list.status_code, 200)
        quiz = quiz_list.json["quizzes"][0]
        self.assertEqual(len(quiz["questions"]), 8)
        self.assertNotIn("answer_index", quiz["questions"][0])
        self.assertEqual(self.client.get(f"/api/quizzes/{quiz['_id']}", headers=headers).status_code, 200)

        result = self.client.post(f"/api/quizzes/{quiz['_id']}/submit", headers=headers,
                                  json={"answers": [1, 0, 0, 0, 0, 0, 0, 0], "elapsed_seconds": 240})
        self.assertEqual(result.status_code, 200)
        self.assertEqual((result.json["attempt"]["score"], result.json["attempt"]["max_score"], result.json["attempt"]["percentage"]), (1, 8, 13))
        self.assertTrue(result.json["review"][0]["correct"])
        self.assertNotIn("answer_index", result.json["attempt"])

        progress = self.client.get("/api/progress", headers=headers)
        self.assertEqual(progress.status_code, 200)
        self.assertEqual(progress.json["summary"]["attempts"], 1)
        self.assertEqual(progress.json["summary"]["average"], 13)
        self.assertEqual(progress.json["topics"][0]["mastery"], 13)
        generated = self.client.post("/api/study-plan/generate", headers=headers, json={})
        self.assertEqual(generated.status_code, 200)
        self.assertEqual(generated.json["plan"]["daily_minutes"], 45)
        self.assertEqual(generated.json["plan"]["tasks"][0]["topic"], "DSA - Foundations")
        self.assertTrue(self.client.get("/api/study-plan", headers=headers).json["plan"]["tasks"])

        recommendations = self.client.get("/api/recommendations", headers=headers)
        self.assertEqual(recommendations.status_code, 200)
        self.assertEqual(recommendations.json["based_on_attempts"], 1)
        self.assertEqual(recommendations.json["topic_guidance"][0]["proficiency_status"], "Weak")
        self.assertFalse(recommendations.json["model"]["available"])

        # New app instance and session over the same database simulate restart + relogin.
        restarted = create_app({"TESTING": True, "MONGODB_CLIENT": self.mongo,
                                "MONGODB_DB": "nebula_acceptance",
                                "JWT_SECRET_KEY": "isolated-acceptance-secret-long-enough-2026",
                                "ADMIN_SIGNUP_KEY": "isolated-admin-invitation-2026"}).test_client()
        login = restarted.post("/api/auth/login", json={"email": "student@example.test", "password": "Long-test-password-2026"})
        self.assertEqual(login.status_code, 200)
        persisted = restarted.get("/api/progress", headers=auth(login.json["access_token"]))
        self.assertEqual(persisted.status_code, 200)
        self.assertEqual(persisted.json["summary"]["attempts"], 1)
        self.assertEqual(self.db.attempts.count_documents({}), 1)

    def test_admin_crud_student_isolation_and_suspension(self):
        student = register(self.client, email="learner@example.test")
        student_headers = auth(student.json["access_token"])
        self.assertEqual(self.client.post("/api/courses", headers=student_headers, json={"course_id": "NEW", "title": "Unauthorized"}).status_code, 403)
        self.assertEqual(self.client.post("/api/quizzes", headers=student_headers, json={"title": "Unauthorized", "questions": []}).status_code, 403)
        self.assertEqual(self.client.post("/api/admin/lessons", headers=student_headers, json={}).status_code, 403)
        self.assertEqual(register(self.client, role="admin", email="blocked-admin@example.test", admin_signup_key="wrong-key").status_code, 403)
        admin = register(self.client, role="admin", email="admin@example.test", admin_signup_key="isolated-admin-invitation-2026")
        self.assertEqual(admin.status_code, 201)
        admin_headers = auth(admin.json["access_token"])
        duplicate_course = self.client.post("/api/courses", headers=admin_headers, json={
            "course_id": "DSA", "title": "Would overwrite DSA", "topics": ["Wrong topic"],
        })
        self.assertEqual(duplicate_course.status_code, 409)
        self.assertEqual(self.db.courses.count_documents({"course_id": "DSA"}), 1)

        course = self.client.post("/api/courses", headers=admin_headers, json={
            "course_id": "WEB-101", "title": "Web Foundations", "subject": "Web",
            "level": "Beginner", "description": "HTML and browser basics.", "estimated_hours": 8,
            "topics": ["HTML", "CSS"],
        })
        self.assertEqual(course.status_code, 201)
        course_topics = self.client.get("/api/courses/WEB-101/topics", headers=student_headers)
        self.assertEqual([row["topic_name"] for row in course_topics.json["topics"]], ["HTML", "CSS"])
        self.assertEqual(self.client.post("/api/courses", headers=admin_headers, json={
            "course_id": "BAD-101", "title": "Bad course", "estimated_hours": "not-a-number", "topics": ["Topic"],
        }).status_code, 400)
        changed_topics = self.client.put("/api/courses/WEB-101", headers=admin_headers, json={
            "topics": ["HTML", "CSS", "Accessibility"],
        })
        self.assertEqual(changed_topics.status_code, 200)
        self.assertEqual(len(self.client.get("/api/courses/WEB-101/topics", headers=student_headers).json["topics"]), 3)
        edited_course = self.client.put("/api/courses/WEB-101", headers=admin_headers, json={"title": "Web Foundations Updated"})
        self.assertEqual(edited_course.json["course"]["title"], "Web Foundations Updated")

        web_lesson = self.client.post("/api/admin/lessons", headers=admin_headers, json={
            "course_id": "WEB-101", "topic_id": "WEB-101_T1", "title": "HTML basics",
            "summary": "A web lesson.", "content": "Learn semantic HTML.", "position": 1,
        })
        self.assertEqual(web_lesson.status_code, 201)
        blocked_topic_edit = self.client.put("/api/courses/WEB-101", headers=admin_headers, json={"topics": ["Replaced"]})
        self.assertEqual(blocked_topic_edit.status_code, 409)
        self.assertEqual(self.client.delete("/api/courses/WEB-101", headers=admin_headers).status_code, 409)
        self.assertEqual(self.client.delete(f"/api/admin/lessons/{web_lesson.json['lesson']['_id']}", headers=admin_headers).status_code, 200)

        lesson = self.client.post("/api/admin/lessons", headers=admin_headers, json={
            "course_id": "DSA", "topic_id": "DSA_T1", "title": "A first lesson",
            "summary": "An in-app introduction.", "content": "Read this short lesson.", "position": 1, "published": True,
        })
        self.assertEqual(lesson.status_code, 201)
        draft = self.client.post("/api/admin/lessons", headers=admin_headers, json={
            "course_id": "DSA", "topic_id": "DSA_T2", "title": "A private draft",
            "summary": "Not published.", "content": "Draft text.", "position": 2, "published": False,
        })
        self.assertEqual(draft.status_code, 201)
        visible = self.client.get("/api/courses/DSA/lessons", headers=student_headers)
        self.assertEqual([item["title"] for item in visible.json["lessons"]], ["A first lesson"])
        self.assertEqual(self.client.put(f"/api/admin/lessons/{lesson.json['lesson']['_id']}", headers=admin_headers, json={"summary": "Updated lesson summary."}).status_code, 200)
        self.assertEqual(self.client.post(f"/api/lessons/{lesson.json['lesson']['_id']}/complete", headers=student_headers, json={}).status_code, 200)
        self.assertEqual(self.client.get("/api/progress", headers=student_headers).json["summary"]["completed_lessons"], 1)

        created_quiz = self.client.post("/api/quizzes", headers=admin_headers, json={
            "title": "Draft quiz", "course_id": "DSA", "topic": "DSA - Foundations", "published": False,
            "questions": [{"prompt": "Which answer?", "topic": "DSA - Foundations", "options": ["A", "B"], "answer_index": 1}],
        })
        self.assertEqual(created_quiz.status_code, 201)
        quiz_id = created_quiz.json["quiz"]["_id"]
        self.assertEqual(self.client.get(f"/api/quizzes/{quiz_id}", headers=student_headers).status_code, 404)
        self.assertEqual(self.client.put(f"/api/quizzes/{quiz_id}", headers=admin_headers, json={"published": True}).status_code, 200)
        visible_quiz = self.client.get(f"/api/quizzes/{quiz_id}", headers=student_headers)
        self.assertEqual(visible_quiz.status_code, 200)
        self.assertNotIn("answer_index", visible_quiz.json["quiz"]["questions"][0])
        self.assertEqual(self.client.delete(f"/api/quizzes/{quiz_id}", headers=admin_headers).status_code, 200)

        student_id = student.json["user"]["_id"]
        self.assertEqual(self.client.patch(f"/api/admin/students/{student_id}/status", headers=admin_headers, json={"status": "suspended"}).status_code, 200)
        self.assertEqual(self.client.post("/api/auth/login", json={"email": "learner@example.test", "password": "Long-test-password-2026"}).status_code, 403)
        self.assertEqual(self.client.get("/api/progress", headers=student_headers).status_code, 403)
        self.assertEqual(self.client.delete("/api/courses/WEB-101", headers=admin_headers).status_code, 200)
        self.assertEqual(self.db.topics.count_documents({"course_id": "WEB-101"}), 0)
        self.assertEqual(self.db.users.count_documents({"role": "admin"}), 1)

    def test_auth_validation_and_security_headers(self):
        self.assertEqual(self.client.get("/api/progress").status_code, 401)
        self.assertEqual(register(self.client, email="bad-email").status_code, 400)
        self.assertEqual(register(self.client, email="short-password@example.test", password="tiny").status_code, 400)
        self.assertEqual(register(self.client, email="long-password@example.test", password="x" * 129).status_code, 400)
        self.assertEqual(self.client.post("/api/auth/login", json={"email": "nobody@example.test", "password": "x" * 100_000}).status_code, 401)
        self.assertEqual(register(self.client, email="duplicate@example.test").status_code, 201)
        self.assertEqual(register(self.client, email="duplicate@example.test").status_code, 409)
        health = self.client.get("/api/health")
        self.assertEqual(health.status_code, 200)
        self.assertEqual(health.json, {"status": "ok", "database": "connected"})
        self.assertEqual(health.headers["X-Content-Type-Options"], "nosniff")
        self.assertIn("Content-Security-Policy", health.headers)

    def test_production_configuration_rejects_unsafe_defaults(self):
        with self.assertRaisesRegex(RuntimeError, "remote MongoDB"):
            create_app({"TESTING": False, "NEBULA_ENV": "production",
                        "MONGODB_URI": "mongodb://127.0.0.1:27017/nebula",
                        "JWT_SECRET_KEY": "x" * 40, "ADMIN_SIGNUP_KEY": "y" * 30,
                        "FRONTEND_ORIGIN": "https://learn.example.test"})
        with self.assertRaisesRegex(RuntimeError, "HTTPS"):
            create_app({"TESTING": False, "NEBULA_ENV": "production",
                        "MONGODB_URI": "mongodb://db.example.test:27017/nebula",
                        "JWT_SECRET_KEY": "x" * 40, "ADMIN_SIGNUP_KEY": "y" * 30,
                        "FRONTEND_ORIGIN": "http://learn.example.test"})

    def test_curriculum_refresh_preserves_admin_prerequisites(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "courses.csv").write_text(
                "course_code,course_name,category\nTST,Test Course,Science\n", encoding="utf-8"
            )
            (root / "topics.csv").write_text(
                "topic_id,course_code,topic_name,difficulty_level,estimated_hours\nTST_T1,TST,Topic One,Beginner,1\n"
                "TST_T2,TST,Topic Two,Beginner,1\n", encoding="utf-8"
            )
            (root / "topic_prerequisite.csv").write_text(
                "id,topic_id,prerequisite_topic_id,prerequisite_type\nTST_EDGE,TST_T2,TST_T1,Direct\n", encoding="utf-8"
            )
            self.db.prerequisites.insert_one({
                "edge_id": "ADMIN_EDGE", "topic_id": "ADMIN_T2",
                "prerequisite_topic_id": "ADMIN_T1", "prerequisite_type": "Direct", "source": "admin",
            })
            import_curriculum(self.db, root)
            self.assertEqual(self.db.prerequisites.count_documents({"edge_id": "ADMIN_EDGE"}), 1)
            self.assertEqual(self.db.prerequisites.count_documents({"edge_id": "TST_EDGE"}), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
