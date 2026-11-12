# Nebula

**Personalized learning, one focused step at a time.**

Nebula is an AI-assisted learning MVP. Students take topic-based quizzes, see where they need practice, and get a study plan shaped by their results. Teachers and administrators manage the courses, lessons, quizzes, and student access.

## Live app

- **Student and admin app:** [nebula-orbit.netlify.app](https://nebula-orbit.netlify.app)
- **Backend health:** [nebula-orbit.onrender.com/api/health](https://nebula-orbit.onrender.com/api/health)

The backend runs on Render and stores application data in MongoDB Atlas. Netlify serves the frontend and proxies `/api/*` requests to Render. The free Render instance can sleep when inactive, so the first request after a quiet period may take longer to respond.

## What Nebula does

### For students

- Create an account and choose a supported B.Tech learning focus and daily study time.
- Explore courses, enroll, and open topic-linked lessons and video resources.
- Take quizzes, review results, and keep an attempt history.
- Track progress and topic mastery over time.
- Get a rule-based study plan and recommendations based on quiz scores and course prerequisites.
- Set available weekdays and a preferred session length; generated sessions respect the selected days and daily time budget.

### For administrators

- Create and update courses, quizzes, and lessons.
- Publish or edit learning content for students.
- Review student account status and aggregate activity.
- Suspend or restore student access.

Admin signup requires the private `ADMIN_SIGNUP_KEY` configured on the server. Never put this key in frontend code or publish it in this README.

## How recommendations work

Study plans currently use quiz scores, weak topics, and prerequisite order. This keeps recommendations explainable and avoids presenting uncertain model output as fact.

Nebula also includes an experimental score estimator trained on historical assessment data. It is evaluated using a chronological holdout, with metrics in [`backend/performance_model_metrics.json`](backend/performance_model_metrics.json). Its forecasts are withheld from students until the model demonstrates a meaningful improvement over a baseline. Score prediction metrics do not prove that a recommended lesson causes learning gains.

## Technology

| Area | Technology |
|---|---|
| Frontend | HTML, CSS, JavaScript |
| API | Python, Flask, Flask-JWT-Extended |
| Database | MongoDB Atlas / MongoDB Community Server |
| ML | pandas-compatible CSV workflow, scikit-learn |
| Local production server | Gunicorn |
| Hosting | Netlify (frontend), Render (API), MongoDB Atlas (database) |

## Run locally

### MongoDB-backed development

Requirements: Python 3.10+ and a running MongoDB instance or Atlas connection string.

1. Copy `backend/.env.example` to `backend/.env`.
2. Set `MONGODB_URI`, `MONGODB_DB`, `JWT_SECRET_KEY`, and `ADMIN_SIGNUP_KEY` in `backend/.env`. Use private, random secrets; do not commit `.env`.
3. Install dependencies and start the API from the repository root:

   ```powershell
   cd backend
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   python app.py
   ```

4. Open [http://127.0.0.1:5000](http://127.0.0.1:5000). Check the database connection at [http://127.0.0.1:5000/api/health](http://127.0.0.1:5000/api/health).

On macOS/Linux, activate the environment with `source .venv/bin/activate` instead.

### Local demo without MongoDB

From the repository root on Windows, run:

```powershell
powershell -ExecutionPolicy Bypass -File .\backend\start-demo.ps1
```

Demo mode uses a local `.demo_data.json` snapshot so accounts and quiz attempts survive a server restart. It is for one developer process only; use MongoDB for shared or real student data. Keep the demo snapshot as a backup until you have verified any migration you need.

## Dataset and model workflows

The supplied CSV files live in `backend/`:

- `courses.csv` — course catalog
- `topics.csv` — course topic catalog
- `topic_prerequisite.csv` — prerequisite relationships
- `student_interaction.csv` — historical assessment records

With MongoDB configured, import the curriculum from `backend/`:

```powershell
python import_dataset.py
```

To include historical assessment rows, set a private `DATASET_HASH_SALT` with at least 24 characters before importing. The importer omits student names and pseudonymizes student and interaction IDs; historical rows are not linked to app login accounts.

To retrain the experimental score estimator after changing the assessment data:

```powershell
python train_performance_model.py
```

Review the reported holdout metrics and `performance_model_metrics.json` before using a new model. Training accuracy alone is not a reliable measure of future performance.

## Deployments

### Frontend — Netlify

- Connect the GitHub repository and deploy the `main` branch.
- Set the publish directory to `frontend`; no frontend build command is required.
- Keep the root [`netlify.toml`](netlify.toml) file. It maps the app's `/assets/*` paths to the published files, proxies `/api/*` to Render, and supports frontend routes.
- The configured API proxy points to `https://nebula-orbit.onrender.com`.

### Backend — Render

- Create a Docker web service from the repository root using the root `Dockerfile`.
- Add the required environment variables in Render's Environment settings (see below).
- Set the health check path to `/api/health`.
- Add the Render service's outbound IP ranges to the Atlas project's **Network Access** IP access list. Avoid `0.0.0.0/0` for production.

### MongoDB Atlas

- Use a dedicated database user with only the privileges Nebula needs.
- Set the Atlas URI as the `MONGODB_URI` secret in Render and use `nebula` for `MONGODB_DB`.
- Keep the cluster active and confirm Atlas network access allows the Render service's outbound ranges.
- Configure backups/retention appropriate to your data before onboarding real students.

### Render environment variables

| Variable | Purpose |
|---|---|
| `NEBULA_ENV` | Set to `production` |
| `NEBULA_DEMO_MODE` | Set to `false` |
| `MONGODB_URI` | Private Atlas connection string |
| `MONGODB_DB` | Database name, normally `nebula` |
| `JWT_SECRET_KEY` | Private signing secret, at least 32 characters |
| `ADMIN_SIGNUP_KEY` | Private administrator invitation key, at least 24 characters |
| `FRONTEND_ORIGIN` | `https://nebula-orbit.netlify.app` (no trailing slash) |

Set secrets only in the hosting provider's secret/environment settings. Do not commit `.env`, database credentials, or signing keys. Rotate credentials that have been exposed in screenshots, chats, or logs.

## API overview

All routes are under `/api`. Protected endpoints require `Authorization: Bearer <access_token>`.

| Feature | Routes |
|---|---|
| Health | `GET /api/health` |
| Authentication and profile | `POST /api/auth/register`, `POST /api/auth/login`, `GET /api/auth/me`, `PATCH /api/auth/profile` |
| Courses and enrollment | `GET /api/courses`, `POST /api/courses`, `PUT/DELETE /api/courses/:course_id`, `GET /api/enrollments`, `POST/DELETE /api/enrollments/:course_id` |
| Lessons | `GET /api/courses/:course_id/lessons`, `GET/POST /api/admin/lessons`, `PUT/DELETE /api/admin/lessons/:id`, `POST /api/lessons/:id/complete` |
| Quizzes | `GET /api/quizzes`, `GET /api/quizzes/:id`, `POST /api/quizzes`, `PUT/DELETE /api/quizzes/:id`, `POST /api/quizzes/:id/submit` |
| Learning | `GET /api/progress`, `GET/POST /api/study-plan`, `POST /api/study-plan/generate`, `GET /api/recommendations` |
| Admin | `GET /api/admin/overview`, `GET /api/admin/students`, `PATCH /api/admin/students/:id/status` |

Student quiz responses omit answer keys. Grading feedback is returned after submission. Admin student views expose profile preferences and aggregate activity, not password hashes or quiz answers. Draft lessons are admin-only; published lessons are available to students.

## Project layout

```text
backend/       Flask API, data import, model workflow, and backend tests
frontend/      Static app (index.html, app.js, style.css)
Dockerfile     Render/Gunicorn container configuration
netlify.toml   Frontend asset, API proxy, and route rules
```

## Tests

Run the backend suite from `backend/`:

```powershell
python -m unittest discover -s tests -v
```

The suite uses an isolated in-memory Mongo mock and does not write test data to Atlas.
