"""Load Nebula's curated pilot question bank from its CSV source."""
from __future__ import annotations

import csv
import json
import re
from datetime import date, datetime, time, timezone
from pathlib import Path
from urllib.parse import urlparse


DATA_DIR = Path(__file__).resolve().parents[1] / "data"
QUESTION_BANK = DATA_DIR / "practice_question_bank.csv"


def curated_practice_quizzes():
    """Return validated, topic-linked quiz documents from the CSV question bank."""
    data_root = DATA_DIR
    known_courses = {
        row["course_code"].strip().upper()
        for filename in ("courses.csv", "branch_curriculum.csv")
        for row in csv.DictReader((data_root / filename).open("r", encoding="utf-8-sig", newline=""))
    }
    mapped_courses = {
        row["course_code"].strip().upper()
        for filename in ("course_tracks.csv", "branch_curriculum.csv")
        for row in csv.DictReader((data_root / filename).open("r", encoding="utf-8-sig", newline=""))
    }
    known_course_topics = {
        (row["course_code"].strip().upper(), row["topic_name"].strip())
        for row in csv.DictReader((data_root / "topics.csv").open("r", encoding="utf-8-sig", newline=""))
    }
    curriculum_topics = set()
    for row in csv.DictReader((data_root / "branch_curriculum.csv").open("r", encoding="utf-8-sig", newline="")):
        course_id = row["course_code"].strip().upper()
        row_topics = {(course_id, name.strip()) for name in row["topics"].split("|") if name.strip()}
        curriculum_topics.update(row_topics)
        known_course_topics.update(row_topics)
    # Every active topic outline, including the older core-course catalog,
    # must have at least one topic-linked practice question.
    curriculum_topics.update(known_course_topics)

    grouped = {}
    covered_curriculum_topics = set()
    with QUESTION_BANK.open("r", encoding="utf-8-sig", newline="") as stream:
        for row_number, row in enumerate(csv.DictReader(stream), 2):
            try:
                options = json.loads(row["options_json"])
                answer_index = int(row["answer_index"])
            except (KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
                raise ValueError(f"Invalid answer/options in {QUESTION_BANK.name}:{row_number}.") from error
            if (not row.get("course_id", "").strip() or not row.get("quiz_title", "").strip()
                    or not row.get("quiz_topic", "").strip() or not row.get("question_topic", "").strip()
                    or not row.get("prompt", "").strip() or not row.get("explanation", "").strip()
                    or not isinstance(options, list) or len(options) != 4
                    or not all(isinstance(option, str) and option.strip() for option in options)
                    or not 0 <= answer_index < len(options)):
                raise ValueError(f"Incomplete question or invalid answer in {QUESTION_BANK.name}:{row_number}.")

            review_status = row.get("review_status", "pending").strip().lower() or "pending"
            reviewer_name = row.get("reviewer_name", "").strip()
            reviewer_role = row.get("reviewer_role", "").strip().lower()
            source_url = row.get("source_url", "").strip()
            review_notes = row.get("review_notes", "").strip()
            review_date_text = row.get("review_date", "").strip()
            review_date = None
            if review_status not in {"pending", "approved", "needs_revision"}:
                raise ValueError(f"Invalid review_status in {QUESTION_BANK.name}:{row_number}.")
            if review_status == "approved":
                parsed_source = urlparse(source_url)
                if (not reviewer_name or reviewer_role not in {"instructor", "subject_matter_expert"}
                        or parsed_source.scheme != "https" or not parsed_source.netloc):
                    raise ValueError(f"Approved question in {QUESTION_BANK.name}:{row_number} needs reviewer name, instructor/subject_matter_expert role, and an HTTPS source URL.")
                try:
                    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", review_date_text):
                        raise ValueError
                    review_date = date.fromisoformat(review_date_text)
                except ValueError as error:
                    raise ValueError(f"Approved question in {QUESTION_BANK.name}:{row_number} needs review_date in YYYY-MM-DD format.") from error

            course_id = row["course_id"].strip().upper()
            question_topic = row["question_topic"].strip()
            if course_id not in known_courses:
                raise ValueError(f"Unknown course {course_id} in {QUESTION_BANK.name}:{row_number}.")
            if course_id not in mapped_courses:
                raise ValueError(f"Course {course_id} has no program-track mapping in {QUESTION_BANK.name}:{row_number}.")
            if (course_id, question_topic) not in known_course_topics:
                raise ValueError(f"Question topic is not in the course outline in {QUESTION_BANK.name}:{row_number}.")
            if (course_id, question_topic) in curriculum_topics:
                covered_curriculum_topics.add((course_id, question_topic))
            quiz_topic = row["quiz_topic"].strip()
            if quiz_topic != "Course-wide practice" and (course_id, quiz_topic) not in known_course_topics:
                raise ValueError(f"Quiz topic is not in the course outline in {QUESTION_BANK.name}:{row_number}.")
            seed_key = f"nebula-practice-v1:{course_id}"
            quiz = grouped.setdefault(seed_key, {
                "seed_key": seed_key,
                "title": row["quiz_title"].strip(),
                "course_id": course_id,
                "topic": row["quiz_topic"].strip(),
                "difficulty": row.get("difficulty", "mixed").strip() or "mixed",
                "assessment_type": "topic_practice",
                "description": "A focused practice set with explanations. Use it to check understanding; it is not a complete exam syllabus.",
                "source": "Nebula-authored starter practice",
                "content_review_status": "instructor_review_pending",
                "published": True,
                "questions": [],
            })
            if quiz["title"] != row["quiz_title"].strip() or quiz["topic"] != quiz_topic:
                raise ValueError(f"Conflicting quiz metadata in {QUESTION_BANK.name}:{row_number}.")
            if any(existing["prompt"].casefold() == row["prompt"].strip().casefold() for existing in quiz["questions"]):
                raise ValueError(f"Duplicate question in {QUESTION_BANK.name}:{row_number}.")
            if len({option.casefold() for option in options}) != len(options):
                raise ValueError(f"Duplicate answer options in {QUESTION_BANK.name}:{row_number}.")
            quiz["questions"].append({
                "prompt": row["prompt"].strip(),
                "topic": question_topic,
                "options": [option.strip() for option in options],
                "answer_index": answer_index,
                "explanation": row["explanation"].strip(),
                "review_status": review_status,
                "reviewer_name": reviewer_name,
                "reviewer_role": reviewer_role,
                "source_url": source_url,
                "review_notes": review_notes,
                "review_date": review_date_text,
                "_review_date": review_date,
            })

    if not grouped:
        raise ValueError(f"The question bank {QUESTION_BANK.name} is empty.")
    missing_topics = curriculum_topics - covered_curriculum_topics
    if missing_topics:
        examples = ", ".join(f"{course_id}:{topic}" for course_id, topic in sorted(missing_topics)[:8])
        raise ValueError(f"Question bank is missing {len(missing_topics)} listed course topics; examples: {examples}.")
    for quiz in grouped.values():
        if len(quiz["questions"]) < 3:
            raise ValueError(f"Quiz {quiz['title']!r} needs at least three questions.")
        if quiz["topic"] == "Course-wide practice":
            quiz["description"] = f"A {len(quiz['questions'])}-question course-wide practice set. Each question is tagged to its own outline topic and includes an explanation. This is starter practice, not a complete exam syllabus."
        else:
            quiz["description"] = f"A {len(quiz['questions'])}-question topic practice set with explanations. Use it to check understanding; it is not a complete exam syllabus."
        statuses = {question["review_status"] for question in quiz["questions"]}
        if statuses == {"approved"}:
            quiz["content_review_status"] = "instructor_reviewed"
            latest_review_date = max(question["_review_date"] for question in quiz["questions"])
            quiz["reviewed_at"] = datetime.combine(latest_review_date, time.min, tzinfo=timezone.utc)
        elif "needs_revision" in statuses:
            quiz["content_review_status"] = "review_revisions_needed"
        else:
            quiz["content_review_status"] = "instructor_review_pending"
        for question in quiz["questions"]:
            question.pop("_review_date", None)
        quiz["created_at"] = datetime.now(timezone.utc)
    return list(grouped.values())
