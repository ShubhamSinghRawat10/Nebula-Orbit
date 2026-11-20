"""Read-only 3-fold grouped CV for live assessment proficiency bands.

Fetches live attempts in memory, creates prior-history-only features, and
prints aggregate metrics. It never exports attempts or writes model artifacts.
"""
from __future__ import annotations

import csv
import json
import os
import sys
from collections import Counter, defaultdict
from datetime import date, datetime
from pathlib import Path

from dotenv import load_dotenv
from pymongo import MongoClient
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction import DictVectorizer
from sklearn.metrics import accuracy_score, balanced_accuracy_score, confusion_matrix, f1_score, roc_auc_score
from sklearn.model_selection import StratifiedGroupKFold, StratifiedKFold

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from core.performance_model import build_features


def score_band(score: float) -> str:
    return "Weak" if score < 50 else "Intermediate" if score < 80 else "Mastered"


def main() -> int:
    load_dotenv(ROOT / ".env")
    uri = os.getenv("MONGODB_URI", "").strip()
    database_name = os.getenv("MONGODB_DB", "").strip()
    if not uri or not database_name:
        print("Missing MONGODB_URI or MONGODB_DB in backend/.env.", file=sys.stderr)
        return 2

    topic_catalog: dict[tuple[str, str], tuple[str, str]] = {}
    with (ROOT / "data" / "topics.csv").open("r", encoding="utf-8-sig", newline="") as stream:
        for topic in csv.DictReader(stream):
            topic_catalog[(topic["course_code"].strip().upper(), topic["topic_name"].strip())] = (
                topic["topic_id"].strip(), topic["difficulty_level"].strip()
            )

    client = None
    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=8000, connectTimeoutMS=8000)
        client.admin.command("ping")
        attempts = list(client[database_name]["attempts"].find(
            {},
            {"_id": 1, "student_id": 1, "course_id": 1, "topic": 1,
             "topic_scores": 1, "score": 1, "max_score": 1, "created_at": 1},
        ))
    except Exception as exc:
        print(f"Could not read live attempts ({type(exc).__name__}); verify Atlas connectivity and access list.", file=sys.stderr)
        return 3
    finally:
        if client is not None:
            client.close()

    rows = []
    unmatched = 0
    for attempt in attempts:
        learner = attempt.get("student_id")
        course = str(attempt.get("course_id") or "").strip().upper()
        attempt_id = attempt.get("_id")
        assessed = attempt.get("created_at")
        if learner is None or attempt_id is None or not course or assessed is None:
            continue
        try:
            day = (assessed.date() if isinstance(assessed, datetime) else assessed if isinstance(assessed, date)
                   else datetime.fromisoformat(str(assessed).replace("Z", "+00:00")).date())
        except (TypeError, ValueError):
            continue
        breakdown = attempt.get("topic_scores") or [{
            "topic": attempt.get("topic", ""), "score": attempt.get("score", 0),
            "max_score": attempt.get("max_score", 0),
        }]
        for result in breakdown:
            try:
                maximum = float(result.get("max_score", 0))
                raw_score = float(result.get("score", 0))
            except (TypeError, ValueError):
                continue
            if maximum <= 0:
                continue
            score = max(0.0, min(100.0, 100.0 * raw_score / maximum))
            topic_name = str(result.get("topic") or "").strip()
            mapped = topic_catalog.get((course, topic_name))
            if mapped:
                topic_id, difficulty = mapped
            else:
                topic_id, difficulty = f"LIVE_{course}_{topic_name}", "Unknown"
                unmatched += 1
            rows.append({
                "learner": str(learner), "day": day, "attempt": str(attempt_id),
                "course": course, "topic": topic_id, "difficulty": difficulty,
                "score": score, "label": score_band(score),
            })

    rows.sort(key=lambda row: (row["learner"], row["day"], row["attempt"], row["topic"]))
    histories: dict[str, list[dict]] = defaultdict(list)
    features, labels, groups = [], [], []
    learner_days: dict[tuple[str, date], list[dict]] = defaultdict(list)
    for row in rows:
        learner_days[(row["learner"], row["day"])].append(row)
    # A learner's same-day results cannot leak into another result from that day.
    for (learner, day), batch in sorted(learner_days.items(), key=lambda item: item[0]):
        pending = []
        for row in batch:
            features.append(build_features(
                histories[learner], row["course"], row["topic"], row["difficulty"], {}, day
            ))
            labels.append(row["label"])
            groups.append(learner)
            pending.append({"score": row["score"], "course_id": row["course"], "topic_id": row["topic"], "date": day})
        histories[learner].extend(pending)

    class_names = ["Weak", "Intermediate", "Mastered"]
    label_counts = Counter(labels)
    learner_count = len(set(groups))
    if len(rows) < 30 or learner_count < 3 or any(label_counts[name] == 0 for name in class_names):
        print(json.dumps({
            "error": "Insufficient rows, learners, or score bands for grouped 3-fold evaluation.",
            "rows": len(rows), "learners": learner_count,
            "label_counts": dict(label_counts), "unmatched_topic_rows": unmatched,
        }, indent=2))
        return 4

    splitter = StratifiedGroupKFold(n_splits=3, shuffle=True, random_state=42)
    oof_predictions = [None] * len(labels)
    oof_majority = [None] * len(labels)
    oof_probabilities = [None] * len(labels)
    fold_metrics = []
    try:
        splits = list(splitter.split(features, labels, groups))
        for fold, (train_idx, test_idx) in enumerate(splits, start=1):
            vectorizer = DictVectorizer(sparse=True)
            train_matrix = vectorizer.fit_transform([features[i] for i in train_idx])
            test_matrix = vectorizer.transform([features[i] for i in test_idx])
            model = RandomForestClassifier(
                n_estimators=100, max_depth=5, min_samples_split=10,
                min_samples_leaf=5, random_state=42, n_jobs=-1,
            )
            model.fit(train_matrix, [labels[i] for i in train_idx])
            predicted = model.predict(test_matrix)
            majority = Counter(labels[i] for i in train_idx).most_common(1)[0][0]
            probabilities = model.predict_proba(test_matrix)
            for index, prediction, probability in zip(test_idx, predicted, probabilities):
                oof_predictions[index] = prediction
                oof_majority[index] = majority
                oof_probabilities[index] = {name: 0.0 for name in class_names} | dict(zip(model.classes_, probability))
            actual = [labels[i] for i in test_idx]
            fold_metrics.append({
                "fold": fold, "train_rows": len(train_idx), "test_rows": len(test_idx),
                "test_learners": len({groups[i] for i in test_idx}),
                "accuracy": round(accuracy_score(actual, predicted), 4),
                "balanced_accuracy": round(balanced_accuracy_score(actual, predicted), 4),
                "macro_f1": round(f1_score(actual, predicted, labels=class_names, average="macro", zero_division=0), 4),
            })
    except ValueError as exc:
        print(f"Grouped cross-validation could not form valid folds ({type(exc).__name__}).", file=sys.stderr)
        return 5

    try:
        auc = round(roc_auc_score(
            labels, [[oof_probabilities[i][name] for name in class_names] for i in range(len(labels))],
            labels=class_names, multi_class="ovr", average="macro",
        ), 4)
    except ValueError:
        auc = None

    # Compare the WhatsApp-style row-stratified split for reference only.
    # It can leak learners and later dates across folds, so it is not a valid
    # estimate of production performance.
    row_cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)
    row_oof = [None] * len(labels)
    row_baseline = [None] * len(labels)
    for train_idx, test_idx in row_cv.split(features, labels):
        vectorizer = DictVectorizer(sparse=True)
        train_matrix = vectorizer.fit_transform([features[i] for i in train_idx])
        test_matrix = vectorizer.transform([features[i] for i in test_idx])
        model = RandomForestClassifier(
            n_estimators=100, max_depth=5, min_samples_split=10,
            min_samples_leaf=5, random_state=42, n_jobs=-1,
        )
        model.fit(train_matrix, [labels[i] for i in train_idx])
        for index, prediction in zip(test_idx, model.predict(test_matrix)):
            row_oof[index] = prediction
            row_baseline[index] = Counter(labels[i] for i in train_idx).most_common(1)[0][0]

    print(json.dumps({
        "method": "RandomForestClassifier + 3-fold StratifiedGroupKFold grouped by learner",
        "target": "score-derived proficiency bands: Weak <50, Intermediate 50–79, Mastered >=80",
        "rows": len(rows), "learners": learner_count, "label_counts": dict(label_counts),
        "unmatched_topic_rows": unmatched, "fold_metrics": fold_metrics,
        "oof_accuracy": round(accuracy_score(labels, oof_predictions), 4),
        "oof_balanced_accuracy": round(balanced_accuracy_score(labels, oof_predictions), 4),
        "oof_macro_f1": round(f1_score(labels, oof_predictions, labels=class_names, average="macro", zero_division=0), 4),
        "group_fold_majority_baseline_accuracy": round(accuracy_score(labels, oof_majority), 4),
        "macro_roc_auc_ovr": auc,
        "confusion_matrix_labels": class_names,
        "confusion_matrix": confusion_matrix(labels, oof_predictions, labels=class_names).tolist(),
        "row_stratified_diagnostic_only": {
            "accuracy": round(accuracy_score(labels, row_oof), 4),
            "balanced_accuracy": round(balanced_accuracy_score(labels, row_oof), 4),
            "macro_f1": round(f1_score(labels, row_oof, labels=class_names, average="macro", zero_division=0), 4),
            "majority_baseline_accuracy": round(accuracy_score(labels, row_baseline), 4),
            "caveat": "Not a trustworthy live estimate: learners and later assessment dates can appear in training and test folds.",
        },
        "notes": "WhatsApp RandomForest settings; read-only, no raw attempts exported, and no model artifact written. Grouped folds hold out learners; score bands are derived directly from scores.",
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
