# Nebula student experience: system design

## Product goal

Make it obvious what a student should do next: choose a course, learn a topic, practice it, understand the result, and see progress update. Every saved record belongs to the authenticated student. The interface should offer useful next steps without pretending the current experimental ML estimate is certain.

## Supported learner and curriculum scope

The active MVP track is **B.Tech course fundamentals**: learners work from the courses, topics, lessons, quizzes, and prerequisite links actually present in the catalog. The first content pilot pairs lessons and explained focused practice sets for DSA, Python, DBMS, Networks, and OS. The catalog spans several CS, systems, development, security, advanced, and hardware subjects. It is not currently mapped to a named university, branch-specific degree plan, or semester sequence, and it is not a complete GATE or placement preparation course. Do not imply that a short diagnostic quiz is sufficient preparation for a formal exam. Add separate tracks only after their syllabus, topic mapping, question bank, and learning resources exist and have been reviewed.

## Student journey

1. **Create account and set intent.** Student signs up with name, email, password, B.Tech learning focus, goal, level/class, and daily minutes. Profile preferences can be changed later; existing profiles default to the active B.Tech course-fundamentals track.
2. **Choose learning.** The catalog shows every available course. Students explicitly enroll in courses; “My courses” shows enrolled items while “Explore all” remains available.
3. **Study a topic.** Course details show curriculum topics, prerequisites, published lessons, completion state, and relevant video resources. Quiz results link to a published matching lesson when available; otherwise they offer a topic-matched video search. Draft lessons are never visible to students.
4. **Practice.** Published quizzes are marked as baseline checks or focused practice. The initial five-subject practice pilot has eight explained questions per subject; these are formative learning checks. Answer keys stay server-side until submission. Each attempt saves a score and topic breakdown under that student.
5. **Review and adapt.** Results explain answers and surface low-scoring topics. Transparent score bands and prerequisites drive study priorities; the score model is labeled experimental.
6. **Follow the plan.** The plan uses enrolled courses first, actual weak topics next, prerequisites before dependent topics, and fits each session within the student's daily time budget. Every session explains its reason (recent quiz signal, prerequisite, starter topic, or due spaced review). Students can mark a session complete; the completion is saved against that plan session.
7. **Check learning after a session.** A later quiz pairs with the most recently completed, not-yet-checked session for the same student, course, and exact topic. The plan shows the follow-up result. A before/after point change is shown only when both the saved pre-session baseline and the topic's follow-up quiz contain at least three questions. This is a descriptive signal, not evidence that the session caused the change. When enough data exists, the next generated plan schedules a spaced review after 1 day (<50%), 3 days (50–79%), or 7 days (80%+).
8. **Track progress.** Dashboard/progress show quiz averages, topic mastery, lesson completion, score trend, session completion, eligible paired checks, and a calendar-correct active streak, all scoped to the current student.

## State and data ownership

- `users.profile`: active learning track, goal, level, available study days, preferred session length, and daily study minutes.
- `course_enrollments`: one record per student/course, with enrollment time. Course content remains shared; enrollment is private to the student.
- `attempts`: quiz result and topic-level score details keyed by student ID.
- `lesson_completions`: lesson completion keyed by student ID and lesson ID.
- `study_plans`: one latest generated plan per student.
- `study_session_completions`: one idempotent completion per student/session, including its plan, course/topic, selection reason, pre-session mastery/sample size, completion time, and (when available) a single later matching quiz result. A score-change field is stored only for pairs with at least three questions on both sides.
- `student_activity_days`: one record per student per UTC calendar day, recording only the event types and first/last activity timestamps needed for return-rate reporting. No quiz answers are copied into this collection.
- `app_metadata`: stores the UTC start of pilot activity tracking so older accounts are not incorrectly treated as non-returning users.
- `lessons`: shared course content; only published records are student-visible.

Old student profiles without a daily-minutes value use 60 minutes. No enrollment is inferred from historical CSV rows.

## UX rules

- Course catalog and enrolled courses are distinct views. A student can still explore without enrolling.
- Empty states explain the next action; a new student sees an invitation to explore/enroll and take a baseline quiz.
- Course detail remains accessible before enrollment. Enroll/unenroll is explicit and reversible.
- Lessons are grouped under their curriculum topic. Completion is idempotent and can be reviewed after completion.
- Quiz cards show question count and topic; the student cannot fetch correct answers before submitting.
- Label baseline checks and focused practice accurately; never present either as a full exam mock.
- Study plan describes a sequence of short sessions, not guaranteed score improvement. It uses weak topics from enrolled courses first; if there are none, it falls back to courses the student has attempted, then to a starter course. It is not a semester timetable or exam-specific preparation plan.
- Every planned session displays its selection reason. Completing a session is explicit and idempotent; only a later quiz with the same course and exact topic can become its follow-up check. A follow-up is linked once, to the latest eligible completed session.
- Spaced review uses only follow-up checks with at least three questions and schedules the next review after 1, 3, or 7 days according to score band. The interval is a simple MVP heuristic, not a validated forgetting-curve model.
- Learning impact is reported as paired descriptive before/after topic scores, only for at least three questions in both results. It must not be described as causal or guaranteed improvement; small samples remain visible as follow-up results but do not enter the change average.
- Admin pilot reporting includes exact UTC day-1/day-7 return among signups after tracking started, latest-plan completion, and eligible before/after score pairs. Return is an authenticated app open or learning action on the target day. Show eligible counts beside every rate; these pilot metrics are directional and are not a model-accuracy measure.
- Score trend uses local calendar dates; streak includes today or yesterday as the active run and resets after a full missed day.
- UI copy must escape student/course/lesson content and keep layouts usable on mobile and keyboard.

## API boundaries

- `GET /api/enrollments` returns only the signed-in student's enrolled course IDs.
- `POST /api/enrollments/:course_id` and `DELETE /api/enrollments/:course_id` mutate only the signed-in student's enrollment.
- Quiz submissions, progress, recommendations, plans, and lesson completion remain student-role protected and query with the current user's ID.
- `POST /api/study-plan/sessions/:session_id/complete` accepts only a session in the signed-in student's current plan and uses a unique student/session key to make repeat clicks safe. Quiz submission links a later exact course/topic result to an eligible completion; `GET /api/study-plan` and `GET /api/progress` expose the resulting status and aggregate metrics.
- `GET /api/admin/overview` returns aggregate pilot retention, latest-plan completion, and paired learning-check metrics to admins only. Activity rows are student-scoped and the overview does not expose individual activity events.
- Course lesson reads return published lessons only for students.
- Admin access is separate and cannot be reached by a student token.

## Recommendation policy

1. Compute topic mastery from the student's own quiz attempts.
2. Mark below 50% as weak, 50–79% as practice, and 80%+ as mastered.
3. Add prerequisite review before weak topics when curriculum links exist.
4. Keep adaptive study sessions within the B.Tech course-fundamentals track and prefer enrolled courses; when no relevant enrollment exists, use the student's attempted courses before offering a starter topic.
5. Include a clear path to browse the wider catalog without implying that every catalog course belongs to the student's degree branch.
6. Use model score estimates as contextual, explicitly experimental information only; rules remain the actionable source until validation beats a simple baseline.

## Delivery plan and acceptance

1. Design and document the flow, ownership, and recommendation rules.
2. Add private enrollment APIs and explicit catalog/enrolled views.
3. Connect lesson completion and quiz actions to course/topic context.
4. Correct plan priorities, date/streak handling, and honest empty states.
5. Record plan-session completion, pair a later same-topic quiz, explain the before/after sample threshold, and schedule due spaced reviews.
6. Review role checks, student scoping, answer-key privacy, output escaping, and responsive layout.

Acceptance: a new student can register, set preferences, enroll in one of all available courses, study published content, complete a quiz, see a student-only result and refreshed plan, and later return to their saved courses/progress. For a plan session, the student can see its reason, mark it complete, take a later quiz covering the same course/topic, and see the linked follow-up result; the change metric appears only when both topic results have at least three questions. A second student's API token cannot read or mutate the first student's enrollment, attempts, plan, session completion, or lesson completion.

## Out of scope for this MVP

Direct messages, guardian accounts, paid access, formal grading/credits, group/class rosters, teacher feedback, offline sync, and promises of guaranteed academic outcomes. The existing CSV history remains pseudonymized and separate from login accounts.
