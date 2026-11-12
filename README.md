# Nebula

Nebula is a personalized learning MVP for students, with an admin workspace for managing course and quiz content. Study plans use transparent quiz-score thresholds and prerequisite-based sequencing. An offline ML score estimator is evaluated on chronological data, but Nebula withholds its forecasts from students until it demonstrates a meaningful lift over the baseline.

## Current setup

- `backend/`: Flask REST API, MongoDB persistence, JWT sessions and role checks.
- Student accounts can register normally. Admin account creation requires the private `ADMIN_SIGNUP_KEY` configured on the server.
- Students can view published courses and quizzes, submit quiz attempts, update their learning profile, mark lessons complete, see progress, generate a study plan and receive rule-based recommendations.
- Demo mode includes an original 8-question baseline diagnostic for each of the 25 CSV courses. These are starter checks and should be reviewed and expanded before classroom use.
- Quiz results are tagged by topic; a regression model estimates next-assessment scores from prior learner results and the curriculum. Its chronological holdout metrics are saved in `backend/performance_model_metrics.json`.
- Admins can manage courses, quizzes and topic-linked lessons; review student account status and aggregate activity; and suspend/reactivate student access.
- `frontend/`: responsive, API-connected student and admin experience. Styling tokens are in `frontend/style.css`; current palette is midnight black, electric cobalt and acid lime.
- The five-course pilot lesson pack contains 10 original, in-app lessons across DSA, Python, DBMS, Computer Networks and Operating Systems. It is published into the configured MongoDB database by `backend/seed_pilot_lessons.py`; re-running the seed does not overwrite admin edits.
- The UI was authored locally from the project brief and public Stitch workflow descriptions. Stitch account access was not used.

## Run the API

1. Install Python 3.10 or newer. Use MongoDB Community Server (or provide a MongoDB connection URI) for persistent data.
2. Install `backend/requirements.txt` into your Python environment.
3. Copy `backend/.env.example` to `backend/.env`; set unique secret values for `JWT_SECRET_KEY` and `ADMIN_SIGNUP_KEY`.
4. From `backend`, run `python app.py`. The frontend is served at `http://127.0.0.1:5000`.

To train or retrain the score estimator after replacing `student_interaction.csv`, run `python train_performance_model.py` from `backend`, then restart the API. The script holds out later assessment dates for evaluation and reports score MAE/RMSE plus proficiency-band accuracy. These metrics evaluate score prediction, not whether a suggested intervention causes learning gains.

For a quick local demo without installing MongoDB, install `backend/requirements-dev.txt` and set `NEBULA_DEMO_MODE=true`. Demo mode seeds baseline quizzes for the full CSV course catalog and saves a local `.demo_data.json` snapshot so student accounts and quiz attempts survive a server restart. It is intended for one local developer process; use MongoDB for real students or multiple server workers.

On Windows, start the demo from the repository root with `powershell -ExecutionPolicy Bypass -File .\backend\start-demo.ps1`. The script selects the project's `.venv`, adds the local `.deps` packages, enables demo mode, and refuses to start if the configured port is already occupied. Stop the existing Nebula process with `Ctrl+C` in its terminal before restarting so the browser cannot keep talking to an older backend process. For a MongoDB-backed run, use the `.env` settings and start `python app.py` from `backend/` instead.

The four supplied CSV files are in `backend/`. Demo mode loads their course, topic, and prerequisite catalog into the app automatically. With MongoDB configured, run `python import_dataset.py` from `backend/` to persist the catalog. To also import historical assessment records, set a private `DATASET_HASH_SALT` of at least 24 characters. The importer drops `student_name` and HMAC-pseudonymizes student and interaction IDs; these records are not attached to login accounts.

The API listens at `http://127.0.0.1:5000`. Check `/api/health` for the database connection status. Never commit `.env` or share the admin signup key.

## Isolated acceptance checks

From `backend/`, run `python -m unittest discover -s tests -v`. The suite uses an isolated in-memory Mongo mock; it covers student signup/login, answer-key hiding, quiz grading and score persistence, progress and prerequisite-aware study plans, recommendation gates, app restart persistence, admin CRUD and access control, lesson publication/completion, account suspension, validation and security headers. It does not write test data to Atlas.

## Production container

The root `Dockerfile` builds a single-container MVP that serves the frontend and Flask API behind Gunicorn. Build with `docker build -t nebula-mvp .`; run it only after providing these private runtime variables through the hosting provider's secret manager: `NEBULA_ENV=production`, `MONGODB_URI`, `MONGODB_DB`, `JWT_SECRET_KEY` (at least 32 private characters), `ADMIN_SIGNUP_KEY` (at least 24 private characters), and `FRONTEND_ORIGIN` (one or more comma-separated HTTPS origins). The app refuses production startup when the remote database or HTTPS/secret requirements are missing. Keep `NEBULA_DEMO_MODE=false`; do not bake `.env` into the image. Configure the hosting provider for HTTPS and a health check at `/api/health`.

Before opening signup to real students, rotate any Atlas password or app secret that has been pasted into a chat, terminal transcript, issue, or screenshot; create a dedicated Atlas database user scoped to the Nebula cluster and `nebula` database; restrict Atlas network access to the hosting provider's fixed egress IPs where possible; confirm Atlas backups/retention; and do one production smoke test with an owner-controlled account. Deployment still requires the project owner to choose a hosting provider/domain, add the runtime secrets and Atlas network allowlist there, and confirm backups. The app and container are prepared, but this repository cannot create a domain or hosting account on the owner's behalf.

## Main API routes

| Purpose | Routes |
|---|---|
| Signup, login, session, profile | `POST /api/auth/register`, `POST /api/auth/login`, `GET /api/auth/me`, `PATCH /api/auth/profile` |
| Courses | `GET /api/courses`, `POST /api/courses`, `PUT /api/courses/:course_id`, `DELETE /api/courses/:course_id` |
| Student enrollment | `GET /api/enrollments`, `POST/DELETE /api/enrollments/:course_id` |
| Lessons | `GET /api/courses/:course_id/lessons`, admin `GET/POST /api/admin/lessons`, `PUT/DELETE /api/admin/lessons/:id`, `POST /api/lessons/:id/complete` |
| Quizzes | `GET /api/quizzes`, `GET /api/quizzes/:id`, `POST /api/quizzes`, `PUT /api/quizzes/:id`, `DELETE /api/quizzes/:id`, `POST /api/quizzes/:id/submit` |
| Learning | `GET /api/progress`, `POST /api/lessons/:id/complete`, `GET/POST /api/study-plan`, `GET /api/recommendations` |
| Admin | `GET /api/admin/overview`, `GET /api/admin/students`, `PATCH /api/admin/students/:id/status` |

Send the JWT as `Authorization: Bearer <access_token>`. Student quiz responses deliberately omit answer keys; keys are returned only in the submission review after grading. Admin student oversight returns profile preferences and aggregate attempt counts only, not quiz answers or password hashes. Suspended accounts cannot sign in or use student-only API routes. Published lesson content is visible to students; drafts are restricted to admins.
