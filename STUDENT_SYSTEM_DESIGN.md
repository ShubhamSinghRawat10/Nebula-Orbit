# Nebula student experience: system design

## Product goal

Make it obvious what a student should do next: choose a course, learn a topic, practice it, understand the result, and see progress update. Every saved record belongs to the authenticated student. The interface should offer useful next steps without pretending the current experimental ML estimate is certain.

## Student journey

1. **Create account and set intent.** Student signs up with name, email, password, goal, level/class, and daily minutes. Profile preferences can be changed later.
2. **Choose learning.** The catalog shows every available course. Students explicitly enroll in courses; “My courses” shows enrolled items while “Explore all” remains available.
3. **Study a topic.** Course details show curriculum topics, prerequisites, published lessons, completion state, and relevant video resources. Draft lessons are never visible to students.
4. **Practice.** Published quizzes are available by course and topic. Answer keys stay server-side until submission. Each attempt saves a score and topic breakdown under that student.
5. **Review and adapt.** Results explain answers and surface low-scoring topics. Transparent score bands and prerequisites drive study priorities; the score model is labeled experimental.
6. **Follow the plan.** The plan uses enrolled courses first, actual weak topics next, prerequisites before dependent topics, and fits each session within the student's daily time budget. New quiz results refresh the plan.
7. **Track progress.** Dashboard/progress show quiz averages, topic mastery, lesson completion, score trend, and a calendar-correct active streak, all scoped to the current student.

## State and data ownership

- `users.profile`: goal, level, and daily study minutes.
- `course_enrollments`: one record per student/course, with enrollment time. Course content remains shared; enrollment is private to the student.
- `attempts`: quiz result and topic-level score details keyed by student ID.
- `lesson_completions`: lesson completion keyed by student ID and lesson ID.
- `study_plans`: one latest generated plan per student.
- `lessons`: shared course content; only published records are student-visible.

Old student profiles without a daily-minutes value use 60 minutes. No enrollment is inferred from historical CSV rows.

## UX rules

- Course catalog and enrolled courses are distinct views. A student can still explore without enrolling.
- Empty states explain the next action; a new student sees an invitation to explore/enroll and take a baseline quiz.
- Course detail remains accessible before enrollment. Enroll/unenroll is explicit and reversible.
- Lessons are grouped under their curriculum topic. Completion is idempotent and can be reviewed after completion.
- Quiz cards show question count and topic; the student cannot fetch correct answers before submitting.
- Study plan describes a sequence of short sessions, not guaranteed score improvement. Empty-history plans use enrolled courses first, then starter courses.
- Score trend uses local calendar dates; streak includes today or yesterday as the active run and resets after a full missed day.
- UI copy must escape student/course/lesson content and keep layouts usable on mobile and keyboard.

## API boundaries

- `GET /api/enrollments` returns only the signed-in student's enrolled course IDs.
- `POST /api/enrollments/:course_id` and `DELETE /api/enrollments/:course_id` mutate only the signed-in student's enrollment.
- Quiz submissions, progress, recommendations, plans, and lesson completion remain student-role protected and query with the current user's ID.
- Course lesson reads return published lessons only for students.
- Admin access is separate and cannot be reached by a student token.

## Recommendation policy

1. Compute topic mastery from the student's own quiz attempts.
2. Mark below 50% as weak, 50–79% as practice, and 80%+ as mastered.
3. Add prerequisite review before weak topics when curriculum links exist.
4. Prefer enrolled courses for plans and dashboard shortcuts; include a clear path to browse more.
5. Use model score estimates as contextual, explicitly experimental information only; rules remain the actionable source until validation beats a simple baseline.

## Delivery plan and acceptance

1. Design and document the flow, ownership, and recommendation rules.
2. Add private enrollment APIs and explicit catalog/enrolled views.
3. Connect lesson completion and quiz actions to course/topic context.
4. Correct plan priorities, date/streak handling, and honest empty states.
5. Review role checks, student scoping, answer-key privacy, output escaping, and responsive layout.

Acceptance: a new student can register, set preferences, enroll in one of all available courses, study published content, complete a quiz, see a student-only result and refreshed plan, and later return to their saved courses/progress. A second student's API token cannot read or mutate the first student's enrollment, attempts, plan, or lesson completion.

## Out of scope for this MVP

Direct messages, guardian accounts, paid access, formal grading/credits, group/class rosters, teacher feedback, offline sync, and promises of guaranteed academic outcomes. The existing CSV history remains pseudonymized and separate from login accounts.
