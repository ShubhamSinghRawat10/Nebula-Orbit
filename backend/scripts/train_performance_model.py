"""Train/evaluate a chronological next-assessment score regression model."""
from __future__ import annotations

import csv
import json
import math
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import joblib
from sklearn.ensemble import ExtraTreesRegressor, HistGradientBoostingRegressor, RandomForestRegressor
from sklearn.feature_extraction import DictVectorizer
from sklearn.base import clone
from sklearn.linear_model import Ridge
from sklearn.metrics import balanced_accuracy_score, f1_score

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from core.performance_model import build_features

DATA_DIR = ROOT / "data"
MODEL_DIR = ROOT / "models"
DATASET = DATA_DIR / "student_interaction.csv"
TOPICS = DATA_DIR / "topics.csv"
ARTIFACT = MODEL_DIR / "performance_model.joblib"
METRICS = MODEL_DIR / "performance_model_metrics.json"


def band(score):
    return "Weak" if score < 50 else "Intermediate" if score < 80 else "Mastered"


def mean_stats(scores):
    return {"mean": sum(scores) / len(scores), "count": len(scores)} if scores else {"mean": 60.0, "count": 0}


def main(dataset_path=DATASET, artifact_path=ARTIFACT, metrics_path=METRICS):
    with TOPICS.open("r", encoding="utf-8-sig", newline="") as stream:
        topic_rows = list(csv.DictReader(stream))
    topic_info = {row["topic_id"]: {"course_id": row["course_code"].upper(), "difficulty": row["difficulty_level"]} for row in topic_rows}
    with Path(dataset_path).open("r", encoding="utf-8-sig", newline="") as stream:
        raw_rows = list(csv.DictReader(stream))
    rows = []
    for row in raw_rows:
        info = topic_info.get(row["topic_id"], {})
        if info and row["course_code"].upper() != info["course_id"]:
            raise ValueError(f"Course/topic mismatch for {row['interaction_id']}.")
        assessed_at_text = str(row.get("last_assessed_at") or "").strip()
        if assessed_at_text:
            row["assessed_at"] = datetime.fromisoformat(assessed_at_text.replace("Z", "+00:00"))
            row["date"] = row["assessed_at"].date()
        else:
            row["date"] = datetime.strptime(row["last_assessed"], "%Y-%m-%d").date()
            row["assessed_at"] = datetime.combine(row["date"], datetime.min.time())
        row["course_code"] = row["course_code"].upper()
        row["score"] = float(row["test_score"])
        row["difficulty"] = info.get("difficulty", "Unknown")
        rows.append(row)
    rows.sort(key=lambda row: (row["date"], row["assessed_at"].timestamp(), row["student_id"], row["interaction_id"]))

    dates = sorted({row["date"] for row in rows})
    train_index = max(1, int(len(dates) * 0.7))
    test_index = max(train_index + 1, max(2, int(len(dates) * 0.8)))
    if test_index >= len(dates):
        raise RuntimeError("Not enough assessment dates for chronological train/validation/test splits.")
    train_cutoff = dates[train_index]
    test_cutoff = dates[test_index]
    learner_history = defaultdict(list)
    train_population_topic = defaultdict(list)
    train_population_course = defaultdict(list)
    train_population_scores = []
    final_population_topic = defaultdict(list)
    final_population_course = defaultdict(list)
    final_population_scores = []
    train_features, train_targets = [], []
    validation_features, validation_targets = [], []
    validation_topic_baselines, validation_global_baselines = [], []
    validation_last_score_baselines = []
    test_features, test_targets, test_topic_baselines, test_global_baselines = [], [], [], []
    test_last_score_baselines = []
    day_groups = defaultdict(list)
    for row in rows:
        day_groups[row["date"]].append(row)

    def population_state(scores, topics, courses):
        return {
            "global_mean": sum(scores) / len(scores) if scores else 60.0,
            "topics": {key: mean_stats(values) for key, values in topics.items()},
            "courses": {key: mean_stats(values) for key, values in courses.items()},
        }

    def add_population(row, scores, topics, courses):
        scores.append(row["score"])
        topics[row["topic_id"]].append(row["score"])
        courses[row["course_code"]].append(row["score"])

    for day in dates:
        batch = day_groups[day]
        # Three chronological periods: train, validation, and untouched test.
        # All rows on a date share the same prior history and population state.
        if day < train_cutoff:
            prior_population = population_state(train_population_scores, train_population_topic, train_population_course)
        elif day < test_cutoff:
            # Validation simulates a model trained only through train_cutoff.
            prior_population = population_state(train_population_scores, train_population_topic, train_population_course)
        else:
            # Test simulates the selected model retrained through validation.
            prior_population = population_state(final_population_scores, final_population_topic, final_population_course)
        pending_population = []
        # Preserve quiz order within a day when the live export includes its
        # timestamp. All topic scores from the same timestamp are one event,
        # so none can leak into another row from that same quiz. Legacy CSVs
        # without timestamps remain grouped by learner and date.
        event_groups = defaultdict(list)
        for row in batch:
            sid = row["student_id"]
            event_key = row["assessed_at"].timestamp() if str(row.get("last_assessed_at") or "").strip() else None
            event_groups[(sid, event_key)].append(row)
        ordered_events = sorted(
            event_groups.items(),
            key=lambda item: (float("-inf") if item[0][1] is None else item[0][1], item[0][0]),
        )
        for (sid, _event_time), event_rows in ordered_events:
            for row in event_rows:
                topic_id = row["topic_id"]
                features = build_features(learner_history[sid], row["course_code"], topic_id, row["difficulty"], prior_population, day)
                if day < train_cutoff:
                    train_features.append(features)
                    train_targets.append(row["score"])
                elif day < test_cutoff:
                    validation_features.append(features)
                    validation_targets.append(row["score"])
                    validation_topic_baselines.append(features["student_topic_mean"] * 100)
                    validation_global_baselines.append(prior_population["global_mean"])
                    validation_last_score_baselines.append(features["student_last_score"] * 100)
                else:
                    test_features.append(features)
                    test_targets.append(row["score"])
                    test_topic_baselines.append(features["student_topic_mean"] * 100)
                    test_global_baselines.append(prior_population["global_mean"])
                    test_last_score_baselines.append(features["student_last_score"] * 100)
                pending_population.append(row)
            learner_history[sid].extend({
                "score": row["score"], "course_id": row["course_code"],
                "topic_id": row["topic_id"], "date": day,
            } for row in event_rows)
        if day < train_cutoff:
            for row in pending_population:
                add_population(row, train_population_scores, train_population_topic, train_population_course)
        if day < test_cutoff:
            for row in pending_population:
                add_population(row, final_population_scores, final_population_topic, final_population_course)

    if not train_features or not validation_features or not test_features:
        raise RuntimeError("Chronological train/validation/test split produced an empty period.")
    validation_vectorizer = DictVectorizer(sparse=True)
    train_matrix = validation_vectorizer.fit_transform(train_features)
    validation_matrix = validation_vectorizer.transform(validation_features)
    candidates = [
        RandomForestRegressor(n_estimators=160, max_depth=16, min_samples_leaf=6, max_features=0.85, n_jobs=-1, random_state=41),
        ExtraTreesRegressor(n_estimators=160, max_depth=16, min_samples_leaf=6, max_features=0.85, n_jobs=-1, random_state=41),
        HistGradientBoostingRegressor(max_iter=160, max_leaf_nodes=15, min_samples_leaf=35, l2_regularization=3.0, learning_rate=0.07, random_state=41),
        Ridge(alpha=1.0),
        Ridge(alpha=10.0),
        Ridge(alpha=50.0),
    ]
    comparisons = []
    best_candidate = None
    best_validation_mae = float("inf")
    for candidate in candidates:
        candidate_matrix = train_matrix.toarray() if isinstance(candidate, HistGradientBoostingRegressor) else train_matrix
        candidate_validation = validation_matrix.toarray() if isinstance(candidate, HistGradientBoostingRegressor) else validation_matrix
        candidate.fit(candidate_matrix, train_targets)
        candidate_predictions = [min(100.0, max(0.0, float(value))) for value in candidate.predict(candidate_validation)]
        candidate_mae = sum(abs(actual - predicted) for actual, predicted in zip(validation_targets, candidate_predictions)) / len(validation_targets)
        comparisons.append({"model": candidate.__class__.__name__, "validation_mae_points": round(candidate_mae, 3)})
        if candidate_mae < best_validation_mae:
            best_candidate, best_validation_mae = candidate, candidate_mae

    validation_topic_mae = sum(abs(actual - baseline) for actual, baseline in zip(validation_targets, validation_topic_baselines)) / len(validation_targets)
    validation_global_mae = sum(abs(actual - baseline) for actual, baseline in zip(validation_targets, validation_global_baselines)) / len(validation_targets)
    validation_last_score_mae = sum(abs(actual - baseline) for actual, baseline in zip(validation_targets, validation_last_score_baselines)) / len(validation_targets)
    comparisons.extend([
        {"model": "previous_topic_mean_baseline", "validation_mae_points": round(validation_topic_mae, 3)},
        {"model": "previous_student_last_score_baseline", "validation_mae_points": round(validation_last_score_mae, 3)},
        {"model": "training_global_mean_baseline", "validation_mae_points": round(validation_global_mae, 3)},
    ])

    # Select on validation only, then refit once on train+validation before the
    # final test. No test result is used to choose a model.
    fit_features = train_features + validation_features
    fit_targets = train_targets + validation_targets
    vectorizer = DictVectorizer(sparse=True)
    fit_matrix = vectorizer.fit_transform(fit_features)
    test_matrix = vectorizer.transform(test_features)
    estimator = clone(best_candidate)
    estimator_matrix = fit_matrix.toarray() if isinstance(estimator, HistGradientBoostingRegressor) else fit_matrix
    final_test_matrix = test_matrix.toarray() if isinstance(estimator, HistGradientBoostingRegressor) else test_matrix
    estimator.fit(estimator_matrix, fit_targets)
    predictions = [min(100.0, max(0.0, float(value))) for value in estimator.predict(final_test_matrix)]
    mae = sum(abs(actual - predicted) for actual, predicted in zip(test_targets, predictions)) / len(test_targets)
    rmse = math.sqrt(sum((actual - predicted) ** 2 for actual, predicted in zip(test_targets, predictions)) / len(test_targets))
    actual_mean = sum(test_targets) / len(test_targets)
    ss_total = sum((value - actual_mean) ** 2 for value in test_targets)
    r2 = 1 - sum((actual - predicted) ** 2 for actual, predicted in zip(test_targets, predictions)) / ss_total if ss_total else 0
    band_accuracy = sum(band(actual) == band(predicted) for actual, predicted in zip(test_targets, predictions)) / len(test_targets)
    topic_baseline_mae = sum(abs(actual - baseline) for actual, baseline in zip(test_targets, test_topic_baselines)) / len(test_targets)
    last_score_baseline_mae = sum(abs(actual - baseline) for actual, baseline in zip(test_targets, test_last_score_baselines)) / len(test_targets)
    global_baseline_mae = sum(abs(actual - baseline) for actual, baseline in zip(test_targets, test_global_baselines)) / len(test_targets)
    majority_band = max(set(map(band, fit_targets)), key=lambda label: sum(band(score) == label for score in fit_targets))
    majority_accuracy = sum(band(actual) == majority_band for actual in test_targets) / len(test_targets)
    predicted_bands = [band(score) for score in predictions]
    actual_bands = [band(score) for score in test_targets]
    band_balanced_accuracy = balanced_accuracy_score(actual_bands, predicted_bands)
    band_macro_f1 = f1_score(actual_bands, predicted_bands, labels=["Weak", "Intermediate", "Mastered"], average="macro", zero_division=0)
    # Keep weak forecasts out of student-facing UI unless the untouched test
    # shows both a useful score-prediction lift and positive explained variance.
    student_facing_eligible = bool(
        r2 > 0
        and mae <= topic_baseline_mae - 2.0
        and mae <= last_score_baseline_mae - 2.0
        and mae <= global_baseline_mae - 2.0
    )

    population = {
        "global_mean": sum(final_population_scores) / len(final_population_scores),
        "topics": {key: mean_stats(values) for key, values in final_population_topic.items()},
        "courses": {key: mean_stats(values) for key, values in final_population_course.items()},
    }
    metrics = {
        "target": "next_assessment_test_score",
        "split": "chronological 70/10/20 by assessment date; same-day rows stay in one split, and timestamped quiz events within a day use only earlier-event history",
        "training_rows": len(fit_targets),
        "selection_training_rows": len(train_targets),
        "validation_rows": len(validation_targets),
        "test_rows": len(test_targets),
        "train_through": str(train_cutoff.fromordinal(train_cutoff.toordinal() - 1)),
        "validation_from": str(train_cutoff),
        "validation_through": str(test_cutoff.fromordinal(test_cutoff.toordinal() - 1)),
        "test_from": str(test_cutoff),
        "mae_points": round(mae, 3),
        "rmse_points": round(rmse, 3),
        "r2": round(r2, 4),
        "proficiency_band_accuracy": round(band_accuracy, 4),
        "proficiency_band_balanced_accuracy": round(float(band_balanced_accuracy), 4),
        "proficiency_band_macro_f1": round(float(band_macro_f1), 4),
        "majority_band_accuracy_baseline": round(majority_accuracy, 4),
        "baseline_previous_topic_mean_mae_points": round(topic_baseline_mae, 3),
        "baseline_previous_student_last_score_mae_points": round(last_score_baseline_mae, 3),
        "baseline_training_global_mean_mae_points": round(global_baseline_mae, 3),
        "student_facing_eligible": student_facing_eligible,
        "candidate_comparison": comparisons,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    Path(artifact_path).parent.mkdir(parents=True, exist_ok=True)
    Path(metrics_path).parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({"vectorizer": vectorizer, "estimator": estimator, "population": population, "metrics": metrics}, artifact_path, compress=3)
    Path(metrics_path).write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(metrics, indent=2))
    print(f"Saved model: {artifact_path}")
    return metrics


if __name__ == "__main__":
    main()

