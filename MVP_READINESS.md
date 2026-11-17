# Nebula MVP readiness

## Completed in this pass

- [x] Student flow acceptance tests: signup, login after a simulated backend restart, answer-key protection, quiz submission, score, topic mastery, progress, prerequisite-first study plan, rule-based recommendations, and stored attempt.
- [x] Admin and permissions acceptance tests: admin invitation key, course and quiz CRUD, lesson publishing/drafts, student-only visibility, lesson completion, suspension, and rejection of student write access.
- [x] Fixed quiz percentage rounding so 1/8 displays as 13%, consistently in the result, progress average, and topic mastery.
- [x] Disabled the ineligible ML artifact at startup; app rules remain the recommendation source until the model passes its evidence gate.
- [x] Added production startup checks, security response headers, Docker/Gunicorn packaging, and launch instructions.
- [x] Published 10 original in-app pilot lessons for DSA, Python, DBMS, Computer Networks, and Operating Systems. Atlas verification: 25 courses, 25 quizzes, 10 published pilot lessons. Re-running the seed inserted zero duplicates.
- [x] Expanded the CSV question bank to 2,595 explained questions across all 172 quiz sets. Every quiz now has at least 15 questions, and all 860 active course-topic pairs have at least 3 distinct questions. Option count, answer index, option uniqueness, and course/topic linkage were checked. All questions remain pending external instructor review; this is formative starter practice, not a complete or instructor-certified exam bank. This source data has not yet been seeded into the live Atlas database.
- [x] Topic mastery and planner weakness labels require at least 3 distinct questions. Repeated attempts at one prompt do not increase evidence. All 860 active topic pairs now meet this minimum coverage threshold, but item quality and learning effectiveness still require instructor review and real-student pilot data.
- [x] Confirmed Atlas already contains account and activity collections. No legacy snapshot was re-imported; `backend/.demo_data.migrated-backup.json` remains preserved.

## Must be completed before the app is used publicly

- [ ] **Rotate the Atlas database user's password in Atlas.** The prior local connection credential appeared in a tool output; the backend `.env` connection URI has therefore been replaced with a placeholder. The user must finish the password change in Atlas, then paste Atlas's new application connection string into `backend/.env` locally. Do not paste it in chat. Restart Nebula and verify `/api/health` reports connected.
- [ ] **Rotate app session/admin keys:** local `.env` now has newly generated JWT and admin-invitation secrets. Restart the backend; all old JWTs are invalidated. Keep `.env` private and use different secret values in production.
- [ ] **Live browser smoke test after database password rotation:** student sign-in, open one seeded lesson, finish a quiz, confirm the displayed score, progress, and generated plan; then verify admin course/quiz/lesson changes and role restrictions.
- [ ] **Choose hosting and domain:** supply production environment secrets to the provider, configure HTTPS, fixed-egress Atlas access, backups/retention, and `/api/health`. The Docker image is ready, but no provider/domain credentials were supplied, so no cloud deployment was performed.
- [ ] **ML remains experimental:** the current holdout proficiency-band accuracy equals the majority baseline and R² is negative. Score-based rules stay in use. Do not show ML estimates until a future untouched chronological evaluation demonstrates reliable lift. More useful model claims also need real learning outcomes after recommendations, not only quiz labels.
- [ ] **Run the backend acceptance suite before merge:** curriculum mapping, content review, and distinct-question behavior have had syntax and source-data validation only in this pass; the full suite was not run.
- [ ] **Seed and verify the refreshed curriculum and practice bank in Atlas after deployment:** no live MongoDB write was made in this pass. Verify quiz/document counts and manually confirm a student can access branch courses, a topic-matched quiz, its answer explanation, and a generated plan.

## Verification command

From `backend/` run:

```powershell
$env:PYTHONPATH = (Resolve-Path .deps).Path
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

The acceptance suite uses an in-memory Mongo mock and does not write test accounts or attempts to Atlas.
