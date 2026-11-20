"""Load the trained next-assessment score estimator and build leak-safe features."""
from __future__ import annotations

import math
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path

import joblib


def parse_date(value):
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if not value:
        return None
    return datetime.fromisoformat(str(value).replace("Z", "+00:00")).date()


def build_features(history, course_id, topic_id, difficulty, population, as_of=None):
    """Features use only prior results for this learner plus training-set priors."""
    history = sorted(history, key=lambda item: parse_date(item.get("date")) or date.min)
    course_id = str(course_id or "").upper()
    topic_id = str(topic_id or "")
    topic_prior = population.get("topics", {}).get(topic_id, {})
    course_prior = population.get("courses", {}).get(course_id, {})
    global_mean = population.get("global_mean", 60.0)
    pop_topic = float(topic_prior.get("mean", global_mean))
    pop_course = float(course_prior.get("mean", global_mean))
    own_scores = [float(item["score"]) for item in history]
    own_course = [float(item["score"]) for item in history if str(item.get("course_id", "")).upper() == course_id]
    own_topic = [float(item["score"]) for item in history if str(item.get("topic_id", "")) == topic_id]
    prior_dates = [parse_date(item.get("date")) for item in history]
    prior_dates = [item for item in prior_dates if item]
    topic_dates = [parse_date(item.get("date")) for item in history if str(item.get("topic_id", "")) == topic_id]
    topic_dates = [item for item in topic_dates if item]
    latest_date = max(prior_dates) if prior_dates else None
    latest_topic_date = max(topic_dates) if topic_dates else None
    now = parse_date(as_of) or date.today()
    mean = lambda values, fallback: sum(values) / len(values) if values else fallback
    return {
        "course_code": course_id,
        "topic_id": topic_id,
        "difficulty": str(difficulty or "Unknown"),
        "student_mean": mean(own_scores, global_mean) / 100,
        "student_course_mean": mean(own_course, pop_course) / 100,
        "student_topic_mean": mean(own_topic, pop_topic) / 100,
        "student_last_score": (own_scores[-1] if own_scores else global_mean) / 100,
        "population_topic_mean": pop_topic / 100,
        "population_course_mean": pop_course / 100,
        "student_attempt_count": math.log1p(len(own_scores)),
        "student_topic_attempt_count": math.log1p(len(own_topic)),
        "days_since_topic_attempt": min(365, max(0, (now - latest_topic_date).days)) / 365 if latest_topic_date else 1.0,
        "days_since_last_attempt": min(365, max(0, (now - latest_date).days)) / 365 if latest_date else 1.0,
    }


class PerformanceModel:
    def __init__(self, artifact):
        self.vectorizer = artifact["vectorizer"]
        self.estimator = artifact["estimator"]
        self.population = artifact["population"]
        self.metrics = artifact.get("metrics", {})

    @classmethod
    def load(cls, path: str | Path):
        return cls(joblib.load(path))

    def predict_score(self, history, course_id, topic_id, difficulty="Unknown", as_of=None):
        features = build_features(history, course_id, topic_id, difficulty, self.population, as_of)
        matrix = self.vectorizer.transform([features])
        if self.estimator.__class__.__name__ == "HistGradientBoostingRegressor":
            matrix = matrix.toarray()
        score = float(self.estimator.predict(matrix)[0])
        return round(min(100.0, max(0.0, score)), 1)

