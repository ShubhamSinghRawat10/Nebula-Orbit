# Dataset review

## Files and coverage

- `courses.csv`: 25 courses; 6 course categories.
- `topics.csv`: 375 topics; 15 per course; difficulty and estimated study hours included.
- `topic_prerequisite.csv`: 507 typed prerequisite edges (Direct, Recommended, Sequential, Co-requisite).
- `student_interaction.csv`: 25,000 assessments covering 150 student IDs.

All course, topic, and prerequisite references resolve. Topic names and course codes agree across the files. There are no duplicate interaction IDs, and the prerequisite graph has no cycle indicators. Twenty assessments share the same student/topic/date, so those should remain separate attempts rather than be silently collapsed.

## What the assessment labels mean

Every `proficiency_status` exactly follows `test_score`: `Weak` is 15–49, `Intermediate` 50–79, and `Mastered` 80–100. That means a model trained to predict proficiency from score would only learn a fixed threshold rule.

Each proficiency band has three possible `recommendation` labels, each used at roughly one third of the time. The file has no subsequent outcome field showing which recommendation improved a student's score. Nebula therefore uses the transparent score bands and prerequisite graph for now, and does not claim the labels establish which intervention is best.

## Privacy

`student_interaction.csv` contains `student_name`. The importer never stores it. If assessment history is imported into MongoDB, it HMAC-pseudonymizes both student and interaction IDs using `DATASET_HASH_SALT`. These records are not linked to app accounts; that needs a deliberate, verified account-linking workflow.

## Import and later CSV updates

Replace the CSVs in this folder, then:

- In demo mode, restart the Flask server; startup reloads the course/topic/prerequisite catalog from the current CSVs.
- With MongoDB configured, run `python import_dataset.py` from this folder to upsert the catalog. Imported CSV-owned rows removed from the new files are removed from the catalog sync; admin-created courses are preserved.
- Assessment history is only imported when `DATASET_HASH_SALT` is set to a secret of at least 24 characters. Re-running the import updates matching interaction IDs and adds new ones. IDs stay pseudonymized and are not joined to student accounts.

The CSVs include course/topic metadata and historical scores, but no question text or later learning outcome. `train_performance_model.py` predicts a historical learner's next assessment score using only earlier attempts and a chronological date holdout. The model does not use the CSV's `recommendation` labels, which cannot prove recommendation effectiveness. Student-specific live recommendations use that student's Nebula quiz attempts; imported historical identities stay separate and are never linked to accounts.

## Current model status

The trainer selects models on a chronological validation period and reports results on a later untouched test period. The current 70/10/20 evaluation produced 59.13% proficiency-band accuracy, equal to the majority-class baseline, and R² of -0.0012. Although score MAE (14.166 points) is lower than the previous-topic-mean baseline (15.702), the lift is not strong enough for a student-facing forecast. The backend therefore withholds ML score estimates unless a future model has positive R² and improves test MAE by at least 2 points. Quiz-score and prerequisite-based study planning remains active.

An additional chronological diagnostic on 2026-11-12 compared student-history mean, last score, and validation-tuned score-to-band thresholds against the global-mean/majority predictor. The validation-selected history/threshold heuristics did not exceed the majority baseline: validation band accuracy was 58.39%, and the later test period remained 59.13%. The global-mean score baseline had test MAE 14.159 points, marginally better than the current estimator's 14.166. This is no evidence of a usable lift; do not tune against the test period or present the current estimate as personalized predictive AI.

To improve the model, collect repeated real-student assessments plus whether each student completed a suggested lesson or resource and their later score on the same topic. Keep assessment dates and student keys stable and pseudonymous. The current CSV's recommendation labels are not evidence of learning improvement.
