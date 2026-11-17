<div align="center">

# ✦ Nebula

### Learn in your own orbit.

An adaptive B.Tech and BCA learning workspace that turns quiz results into a clear, manageable next step.

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/API-Flask-111111?logo=flask)](https://flask.palletsprojects.com/)
[![MongoDB](https://img.shields.io/badge/Data-MongoDB%20Atlas-47A248?logo=mongodb&logoColor=white)](https://www.mongodb.com/atlas)
[![Netlify](https://img.shields.io/badge/Web-Netlify-00C7B7?logo=netlify&logoColor=white)](https://www.netlify.com/)
[![Render](https://img.shields.io/badge/API%20hosting-Render-46E3B7?logo=render&logoColor=111111)](https://render.com/)

[Open Nebula](https://nebula-orbit.netlify.app) · [API health](https://nebula-orbit.onrender.com/api/health) · [Student system design](STUDENT_SYSTEM_DESIGN.md) · [Admin system design](ADMIN_SYSTEM_DESIGN.md)

</div>

---

## Contents

- [About](#about)
- [What it does](#what-it-does)
- [How personalization works](#how-personalization-works)
- [Technology and architecture](#technology-and-architecture)
- [Run locally](#run-locally)
- [Dataset and model workflow](#dataset-and-model-workflow)
- [Deployment](#deployment)
- [API reference](#api-reference)
- [Project structure](#project-structure)
- [Run the backend acceptance suite](#run-the-backend-acceptance-suite)
- [Security notes](#security-notes)
- [Current scope](#current-scope)

## About

Nebula is an AI-assisted learning MVP for students who want a more focused way to study B.Tech and BCA subjects. Students can choose a supported branch, explore a course, take a topic-based quiz, review their score, and use a personalized study plan to decide what to work on next. Administrators maintain the learning content and manage student access.

**Current learning tracks:** 35 B.Tech branch/specialization choices and a BCA track, backed by a common reference outline. The catalog is not a complete or semester-mapped syllabus for every university. Nebula is not yet a complete GATE or placement-preparation curriculum; those need their own reviewed syllabi, question banks, and resources.

The product keeps recommendations explainable: a student's own quiz history and the curriculum prerequisite graph drive the study plan. The included machine-learning score estimator is experimental and is **not** treated as a reliable student-facing prediction.

## What it does

### Student workspace

- Sign up and sign in with a student account.
- Choose a learning focus, degree/level, and daily study-time budget.
- Set available study days and preferred session length in the profile.
- Plans prioritize weak topics from enrolled courses, then fall back to courses the student has attempted.
- Nebula treats a topic as weak only after at least three distinct questions; smaller samples are shown as preliminary practice signals.
- Choose a B.Tech branch/specialization or BCA track, then explore its assigned course catalog and enroll in courses.
- Read published in-app pilot lessons where available; find topic-specific video resources through YouTube search links.
- Take quizzes, see answer explanations after submission, and review saved attempts.
- Track quiz averages, topic mastery, completed lessons, and study streaks.
- Generate a study plan with a reason for each session (quiz signal, prerequisite, or spaced review), then mark sessions complete.
- Track follow-up quizzes on the same course topic and compare them with the pre-session topic baseline when both contain at least three distinct questions.

### Administrator workspace

- Create, edit, publish, and remove courses and quizzes.
- Draft, publish, edit, and remove lessons linked to course topics.
- Review student account status and high-level activity.
- Suspend and restore student access.

Administrator registration requires the private `ADMIN_SIGNUP_KEY` configured on the backend. It is never included in frontend code or this README.

## How personalization works

1. Quiz attempts are saved to the student's account.
2. Topic-level performance highlights areas for more practice.
3. Course prerequisites help order foundational work before dependent topics.
4. The study planner schedules focused sessions around the student's selected days, session length, and daily time budget.
5. New quiz results can refresh the plan and recommendations.

These recommendations are rule-based and grounded in the student's app activity. They are guidance for study planning, not a guarantee of exam results.

### Experimental ML model

The repository includes a model that estimates a learner's next assessment score from historical assessment data. It uses a chronological train/validation/test split. In the current evaluation, proficiency-band accuracy equals the majority-class baseline, and the model's test R² is negative. The backend therefore does not treat its output as a dependable personalized forecast; score-based rules remain the active planning approach.

See the evaluation details in [`backend/performance_model_metrics.json`](backend/performance_model_metrics.json) and data limitations in [`backend/DATASET_NOTES.md`](backend/DATASET_NOTES.md). Do not tune against the held-out test period.

## Technology and architecture

| Layer | Implementation |
|---|---|
| Frontend | Static HTML, CSS, and JavaScript |
| API and authentication | Python, Flask, Flask-JWT-Extended |
| Database | MongoDB Atlas or local MongoDB |
| Model workflow | pandas-compatible CSV input, scikit-learn |
| Production API server | Gunicorn in Docker |
| Hosting | Netlify frontend, Render API, MongoDB Atlas database |

```mermaid
flowchart LR
    S[Student or admin browser] --> N[Netlify static frontend]
    N -->|/api requests| R[Render Flask API]
    R --> M[(MongoDB Atlas)]
    R --> C[Courses, quizzes, lessons, plans]
```

The frontend sends requests to `/api`. Netlify routes those requests to the Render service, so the browser uses one site origin. The free Render instance may sleep when inactive; its first request after a quiet period can take longer.

## Run locally

### MongoDB-backed app

You need Python 3.10+ and either a running local MongoDB server or an Atlas connection string.

1. Create a private environment file:

   ```powershell
   Copy-Item backend/.env.example backend/.env
   ```

2. Edit `backend/.env` locally. Set `MONGODB_URI`, `MONGODB_DB`, `JWT_SECRET_KEY`, `ADMIN_SIGNUP_KEY`, and `FRONTEND_ORIGIN` for your setup. Use private random secrets; do not paste them into chat or commit the file.

3. Install dependencies and start the API from the `backend` directory:

   ```powershell
   cd backend
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   python app.py
   ```

4. Open [http://127.0.0.1:5000](http://127.0.0.1:5000). Check API and database connectivity at [http://127.0.0.1:5000/api/health](http://127.0.0.1:5000/api/health).

On macOS/Linux, activate the virtual environment with `source .venv/bin/activate`.

### Local demo mode

For a local demo backed by the `.demo_data.json` snapshot, use Windows PowerShell from the repository root:

```powershell
powershell -ExecutionPolicy Bypass -File .\backend\start-demo.ps1
```

Demo mode is for one local developer process, not shared student accounts. Keep the snapshot private and backed up; it may contain personal demo data.

## Dataset and model workflow

The curriculum data and assessment history are in `backend/`:

| File | Purpose |
|---|---|
| `courses.csv` | Course catalog |
| `topics.csv` | Topic catalog and study metadata |
| `topic_prerequisite.csv` | Relationships used to sequence foundational topics |
| `curriculum_tracks.csv` | Supported B.Tech branches/specializations and BCA learning track |
| `course_tracks.csv` | Assigns existing catalog courses to eligible degree tracks |
| `branch_curriculum.csv` | Shared foundations plus authored branch subject/topic outlines |
| `curriculum_track_parents.csv` | Explicit course inheritance for related specializations |
| `build_branch_curriculum.py` | Rebuilds shared engineering foundations and branch outline rows |
| `build_core_course_practice.py` | Replaces generic topics for the shared computing course catalog and writes its topic-linked starter questions |
| `expand_foundation_bca_practice.py` | Adds original, topic-balanced questions for shared B.Tech foundations and all BCA courses |
| `expand_computing_practice.py` | Repeatable source for Nebula-authored question packs across computing and selected B.Tech branch courses |
| `practice_question_bank.csv` | Topic-linked starter questions, choices, answer keys, explanations, and review evidence fields; all authored rows currently remain pending instructor review |
| `student_interaction.csv` | Historical assessment records for analysis/model evaluation |

The current catalog has 35 B.Tech branch/specialization tracks and one BCA track. It is a common reference outline, not a complete or semester-mapped syllabus for every university. Specialist tracks inherit only the parent courses listed in `curriculum_track_parents.csv`. Read [`backend/CURRICULUM_SOURCES.md`](backend/CURRICULUM_SOURCES.md) for the source scope and limitations before using it for exam planning. The question bank has 2,595 explained questions across 172 quiz sets: every quiz has at least 15 questions and all 860 active course-topic pairs have at least three distinct questions. All question records remain pending external instructor review, so treat these as formative starter practice rather than formal exam material. This is not a complete exam-preparation product. In-app lessons are still limited to the pilot subjects.

To import or sync the curriculum into the configured MongoDB database, run from `backend/`:

```powershell
python import_dataset.py
```

To add the pilot lessons and CSV-backed practice quizzes, run from `backend/` after curriculum import:

```powershell
python seed_learning_content.py
```

The seeder validates and imports 172 focused quizzes (2,595 questions) with answer explanations and topic links. Every quiz has at least 15 questions, and every active course-topic pair has at least three. Questions are Nebula-authored starter drafts and have not had external instructor review; they are not full-length semester, GATE, or placement mocks. The seeder is idempotent under its own seed keys, preserves admin-edited quiz content, and extends a source-controlled quiz only when its stored questions exactly match the beginning of the CSV set.

Historical assessment rows are imported only when a private `DATASET_HASH_SALT` is configured. The importer omits student names and pseudonymizes student and interaction IDs. Imported historical identities are not connected to app login accounts.

To retrain the experimental score estimator after changing the data:

```powershell
python train_performance_model.py
```

Review the held-out metrics before using a new artifact. A stronger model needs genuinely predictive features and future learning outcomes; more rows alone do not guarantee better accuracy. Dataset definitions, privacy handling, and limitations are documented in [`backend/DATASET_NOTES.md`](backend/DATASET_NOTES.md).

## Deployment

### Frontend — Netlify

- Connect the GitHub repository and deploy the `main` branch.
- Set the publish directory to `frontend`; no build command is required.
- Keep the root `netlify.toml`: it serves `/assets/*`, proxies `/api/*` to Render, and routes frontend paths to `index.html`.
- Configure `FRONTEND_ORIGIN` on Render to match the deployed site origin, without a trailing slash.

### Backend — Render

- Create a Docker web service from the repository root using the root `Dockerfile`.
- Configure the required environment variables in Render's Environment settings.
- Set the health-check path to `/api/health`.
- Add Render's documented outbound IP ranges to the Atlas Network Access list. Avoid broad `0.0.0.0/0` access for a production database.

### MongoDB Atlas

- Use an application database user with only the permissions required by Nebula.
- Store the connection string as the `MONGODB_URI` secret in Render; set `MONGODB_DB` to the intended database name.
- Confirm Atlas network access permits the Render service to connect.
- Configure backups and retention before onboarding real students.

### Backend environment variables

Set these in the deployment provider's private environment settings. The values belong there, not in source control or README:

| Variable | Purpose |
|---|---|
| `NEBULA_ENV` | Use `production` for the hosted service |
| `NEBULA_DEMO_MODE` | Keep `false` when using MongoDB |
| `MONGODB_URI` | Private MongoDB connection string |
| `MONGODB_DB` | MongoDB database name |
| `JWT_SECRET_KEY` | Private token-signing secret |
| `ADMIN_SIGNUP_KEY` | Private admin invitation key |
| `FRONTEND_ORIGIN` | Exact deployed frontend origin, without trailing slash |

## API reference

Protected routes require `Authorization: Bearer <access_token>`. Admin-only routes additionally require an administrator account.

| Area | Endpoints |
|---|---|
| Health | `GET /api/health` |
| Accounts | `POST /api/auth/register`, `POST /api/auth/login`, `GET /api/auth/me`, `PATCH /api/auth/profile` |
| Courses | `GET /api/courses`, `POST /api/courses`, `PUT/DELETE /api/courses/:course_id` |
| Enrollment and topics | `GET /api/enrollments`, `POST/DELETE /api/enrollments/:course_id`, `GET /api/courses/:course_id/topics` |
| Lessons | `GET /api/courses/:course_id/lessons`, `GET/POST /api/admin/lessons`, `PUT/DELETE /api/admin/lessons/:id`, `POST /api/lessons/:id/complete` |
| Quizzes | `GET /api/quizzes`, `GET /api/quizzes/:id`, `POST /api/quizzes`, `PUT/DELETE /api/quizzes/:id`, `POST /api/quizzes/:id/submit` |
| Student learning | `GET /api/progress`, `GET /api/study-plan`, `POST /api/study-plan/generate`, `POST /api/study-plan/sessions/:session_id/complete`, `GET /api/recommendations` |
| Admin | `GET /api/admin/overview`, `GET /api/admin/students`, `PATCH /api/admin/students/:id/status` |

Quiz answer keys are not sent with the student quiz. Grading feedback is returned after submission. Admin student views contain profile preferences and aggregate activity, not password hashes or answer selections. Draft lessons are only available to admins; published lessons are available to students.

Study-session outcomes are descriptive before/after comparisons. They help monitor whether students return to a topic and how their later quiz score compares with a prior baseline; they do not prove that the plan caused a score change. Score-change summaries require at least three distinct questions in both the baseline and follow-up.

The administrator overview also reports pilot signals: exact UTC day-1/day-7 student return rates, completion across students' latest saved plans, and eligible paired topic-score changes. Return tracking starts when the backend first initializes this feature; earlier accounts are excluded from the retention denominator. Returns count an authenticated app visit or a learning action. These small pilot metrics are directional and should be interpreted with their eligible sample counts, not as evidence of causation or model accuracy.

## Project structure

```text
.
├── backend/                 Flask API, CSV data, model workflow, and tests
│   ├── app.py               API routes, authentication, study planner
│   ├── tests/               Backend acceptance and regression tests
│   ├── *.csv                Curriculum and historical assessment data
│   ├── import_dataset.py    MongoDB curriculum/history importer
│   └── train_performance_model.py
├── frontend/                Static HTML, JavaScript, and CSS
├── Dockerfile               Render/Gunicorn container setup
├── netlify.toml             Netlify publishing, API proxy, and SPA routes
├── STUDENT_SYSTEM_DESIGN.md  Student experience and flow
├── ADMIN_SYSTEM_DESIGN.md   Admin experience and flow
└── MVP_READINESS.md         Current MVP checklist and launch considerations
```

## Run the backend acceptance suite

From `backend/`, install the development dependencies and run the isolated API acceptance tests:

```powershell
pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
```

The suite uses `mongomock` and does not write test users or attempts to your Atlas database.

## Security notes

- `backend/.env` is private local configuration and is ignored by Git.
- Never commit database URIs, passwords, JWT secrets, admin signup keys, or dataset salts.
- Use provider-managed secret settings for Render and keep access limited to project maintainers.
- Rotate any credential that was exposed in a screenshot, terminal capture, chat, or Git history.
- Do not put real student data in public issues, screenshots, or sample files.

## Current scope

- The catalog supports 35 B.Tech branch/specialization tracks and BCA, with common foundation and authored branch subject/topic outlines in CSV.
- In-app lesson content is a pilot set for DSA, Python, DBMS, Computer Networks, and Operating Systems; result pages open a matching published lesson where one exists and otherwise offer a YouTube topic search.
- The CSV-backed bank contains 172 short quizzes and 2,595 explained questions. Every quiz has at least 15 questions, with at least 3 distinct questions in each of 860 listed course-topic pairs. All questions remain pending external instructor review. In-app lessons remain a small pilot library. These are formative practice sets, not complete GATE, semester-exam, or placement-interview mocks.
- Rule-based study planning is active. The ML score estimator remains experimental and is not a promise of student performance.

For the detailed launch checklist and verification status, see [`MVP_READINESS.md`](MVP_READINESS.md).
