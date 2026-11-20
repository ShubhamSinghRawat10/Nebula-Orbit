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
from sklearn.ensemble import ExtraTreesRegressor, HistGradientBoostingRegressor, RandomForestClassifier, RandomForestRegressor
from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import Ridge
from sklearn.metrics import accuracy_score, balanced_accuracy_score, confusion_matrix, f1_score, mean_absolute_error, mean_squared_error, r2_score, roc_auc_score
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
    unmatched_topic_counts: Counter[tuple[str, str]] = Counter()
    for attempt in attempts:
        learner = attempt.get("student_id")
        course = str(attempt.get("course_id") or "").strip().upper()
        attempt_id = attempt.get("_id")
        assessed = attempt.get("created_at")
        if learner is None or attempt_id is None or not course or assessed is None:
            continue
        try:
            if isinstance(assessed, datetime):
                event_time, day = assessed, assessed.date()
            elif isinstance(assessed, date):
                day = assessed
                event_time = datetime.combine(day, datetime.min.time())
            else:
                event_time = datetime.fromisoformat(str(assessed).replace("Z", "+00:00"))
                day = event_time.date()
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
                unmatched_topic_counts[(course, topic_name)] += 1
            rows.append({
                "learner": str(learner), "day": day, "event_time": event_time, "attempt": str(attempt_id),
                "course": course, "topic": topic_id, "difficulty": difficulty,
                "score": score, "label": score_band(score),
            })

    rows.sort(key=lambda row: (row["learner"], row["event_time"].timestamp(), row["attempt"], row["topic"]))
    histories: dict[str, list[dict]] = defaultdict(list)
    features, labels, groups, scores, feature_dates = [], [], [], [], []
    learner_events: dict[tuple[str, float], list[dict]] = defaultdict(list)
    for row in rows:
        learner_events[(row["learner"], row["event_time"].timestamp())].append(row)
    # Same-event topic scores share features; earlier same-day quizzes may inform later ones.
    for (learner, _event_time), batch in sorted(learner_events.items(), key=lambda item: item[0]):
        day = batch[0]["day"]
        pending = []
        for row in batch:
            features.append(build_features(
                histories[learner], row["course"], row["topic"], row["difficulty"], {}, day
            ))
            labels.append(row["label"])
            groups.append(learner)
            scores.append(row["score"])
            feature_dates.append(day)
            pending.append({"score": row["score"], "course_id": row["course"], "topic_id": row["topic"], "date": day})
        histories[learner].extend(pending)

    class_names = ["Weak", "Intermediate", "Mastered"]
    label_counts = Counter(labels)
    learner_count = len(set(groups))
    date_counts = Counter(row["day"].isoformat() for row in rows)
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
    regression_predictions = {
        "RandomForestRegressor": [None] * len(scores),
        "ExtraTreesRegressor": [None] * len(scores),
        "HistGradientBoostingRegressor": [None] * len(scores),
        "previous_student_topic_mean_baseline": [None] * len(scores),
    }
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
            regression_candidates = [
                RandomForestRegressor(n_estimators=160, max_depth=16, min_samples_leaf=6,
                                      max_features=0.85, n_jobs=-1, random_state=41),
                ExtraTreesRegressor(n_estimators=160, max_depth=16, min_samples_leaf=6,
                                    max_features=0.85, n_jobs=-1, random_state=41),
                HistGradientBoostingRegressor(max_iter=160, max_leaf_nodes=15,
                                              min_samples_leaf=35, l2_regularization=3.0,
                                              learning_rate=0.07, random_state=41),
            ]
            for regressor in regression_candidates:
                train_reg_matrix, test_reg_matrix = train_matrix, test_matrix
                if isinstance(regressor, HistGradientBoostingRegressor):
                    train_reg_matrix, test_reg_matrix = train_matrix.toarray(), test_matrix.toarray()
                regressor.fit(train_reg_matrix, [scores[i] for i in train_idx])
                predicted_scores = regressor.predict(test_reg_matrix)
                for index, prediction in zip(test_idx, predicted_scores):
                    regression_predictions[regressor.__class__.__name__][index] = max(0.0, min(100.0, float(prediction)))
            for index in test_idx:
                regression_predictions["previous_student_topic_mean_baseline"][index] = float(features[index]["student_topic_mean"]) * 100.0
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

    regression_metrics = {}
    for name, predicted in regression_predictions.items():
        predicted_bands = [score_band(value) for value in predicted]
        regression_metrics[name] = {
            "mae_points": round(mean_absolute_error(scores, predicted), 3),
            "rmse_points": round(mean_squared_error(scores, predicted) ** 0.5, 3),
            "r2": round(r2_score(scores, predicted), 4),
            "band_accuracy": round(accuracy_score(labels, predicted_bands), 4),
            "band_balanced_accuracy": round(balanced_accuracy_score(labels, predicted_bands), 4),
            "band_macro_f1": round(f1_score(labels, predicted_bands, labels=class_names, average="macro", zero_division=0), 4),
        }

    # Returning-learner use case: rolling-origin folds keep future dates out
    # of training while allowing earlier history from the same learner.
    temporal_dates = sorted(set(feature_dates))[-3:]
    temporal_predictions = {
        name: [None] * len(scores)
        for name in ("RandomForestRegressor", "ExtraTreesRegressor", "HistGradientBoostingRegressor", "Ridge")
    }
    temporal_baselines = {
        name: [None] * len(scores)
        for name in ("previous_student_topic_mean", "previous_student_last_score", "previous_student_mean")
    }
    temporal_fold_metrics = []
    for day in temporal_dates:
        train_idx = [i for i, observed_day in enumerate(feature_dates) if observed_day < day]
        test_idx = [i for i, observed_day in enumerate(feature_dates) if observed_day == day]
        if len(train_idx) < 30 or not test_idx:
            continue
        vectorizer = DictVectorizer(sparse=True)
        train_matrix = vectorizer.fit_transform([features[i] for i in train_idx])
        test_matrix = vectorizer.transform([features[i] for i in test_idx])
        candidates = [
            RandomForestRegressor(n_estimators=160, max_depth=16, min_samples_leaf=6,
                                  max_features=0.85, n_jobs=-1, random_state=41),
            ExtraTreesRegressor(n_estimators=160, max_depth=16, min_samples_leaf=6,
                                max_features=0.85, n_jobs=-1, random_state=41),
            HistGradientBoostingRegressor(max_iter=160, max_leaf_nodes=15,
                                          min_samples_leaf=35, l2_regularization=3.0,
                                          learning_rate=0.07, random_state=41),
            Ridge(alpha=10.0),
        ]
        for candidate in candidates:
            fit_matrix, predict_matrix = train_matrix, test_matrix
            if isinstance(candidate, HistGradientBoostingRegressor):
                fit_matrix, predict_matrix = train_matrix.toarray(), test_matrix.toarray()
            candidate.fit(fit_matrix, [scores[i] for i in train_idx])
            for index, prediction in zip(test_idx, candidate.predict(predict_matrix)):
                temporal_predictions[candidate.__class__.__name__][index] = max(0.0, min(100.0, float(prediction)))
        for index in test_idx:
            for name, feature_name in (
                ("previous_student_topic_mean", "student_topic_mean"),
                ("previous_student_last_score", "student_last_score"),
                ("previous_student_mean", "student_mean"),
            ):
                temporal_baselines[name][index] = float(features[index][feature_name]) * 100.0
        temporal_fold_metrics.append({
            "test_date": day.isoformat(), "train_rows": len(train_idx), "test_rows": len(test_idx),
        })

    temporal_metrics = {}
    temporal_test_idx = [i for i, day in enumerate(feature_dates) if day in temporal_dates and any(
        fold["test_date"] == day.isoformat() for fold in temporal_fold_metrics
    )]
    if temporal_test_idx:
        y_temporal = [scores[i] for i in temporal_test_idx]
        for name, predictions in (temporal_predictions | temporal_baselines).items():
            pred_temporal = [predictions[i] for i in temporal_test_idx]
            temporal_metrics[name] = {
                "mae_points": round(mean_absolute_error(y_temporal, pred_temporal), 3),
                "rmse_points": round(mean_squared_error(y_temporal, pred_temporal) ** 0.5, 3),
                "r2": round(r2_score(y_temporal, pred_temporal), 4),
                "per_date_mae": {
                    fold["test_date"]: round(mean_absolute_error(
                        [scores[i] for i in temporal_test_idx if feature_dates[i].isoformat() == fold["test_date"]],
                        [predictions[i] for i in temporal_test_idx if feature_dates[i].isoformat() == fold["test_date"]],
                    ), 3)
                    for fold in temporal_fold_metrics
                },
            }

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
        "assessment_dates": dict(sorted(date_counts.items())),
        "unmatched_topic_rows": unmatched, "fold_metrics": fold_metrics,
        "most_common_unmatched_topics": [
            {"course_code": course, "topic_label": topic, "rows": count}
            for (course, topic), count in unmatched_topic_counts.most_common(10)
        ],
        "oof_accuracy": round(accuracy_score(labels, oof_predictions), 4),
        "oof_balanced_accuracy": round(balanced_accuracy_score(labels, oof_predictions), 4),
        "oof_macro_f1": round(f1_score(labels, oof_predictions, labels=class_names, average="macro", zero_division=0), 4),
        "group_fold_majority_baseline_accuracy": round(accuracy_score(labels, oof_majority), 4),
        "macro_roc_auc_ovr": auc,
        "grouped_regression_oof_metrics": regression_metrics,
        "rolling_future_date_folds": temporal_fold_metrics,
        "rolling_future_date_oof_metrics": temporal_metrics,
        "confusion_matrix_labels": class_names,
        "confusion_matrix": confusion_matrix(labels, oof_predictions, labels=class_names).tolist(),
        "row_stratified_diagnostic_only": {
            "accuracy": round(accuracy_score(labels, row_oof), 4),
            "balanced_accuracy": round(balanced_accuracy_score(labels, row_oof), 4),
            "macro_f1": round(f1_score(labels, row_oof, labels=class_names, average="macro", zero_division=0), 4),
            "majority_baseline_accuracy": round(accuracy_score(labels, row_baseline), 4),
            "caveat": "Not a trustworthy live estimate: learners and later assessment dates can appear in training and test folds.",
        },
        "notes": "Read-only; no raw attempts exported and no model artifact written. Same-event topic scores share features; earlier same-day quizzes may inform later predictions. Grouped folds hold out learners; score bands are derived directly from scores.",
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
