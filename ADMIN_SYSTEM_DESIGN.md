# Nebula admin tools: system design

## Goal

Give trusted admins a safe way to maintain learner-facing lessons and oversee student accounts, while keeping student data private and preserving the existing course, quiz, and progress flows.

## Roles and access

- Students can read published lessons for their courses, mark published lessons complete, and access only their own learning records.
- Admins can create, edit, publish, unpublish, and remove lessons; list student accounts and their aggregate learning activity; and suspend or reactivate an account.
- Student list responses contain only name, email, account status, signup date, profile preferences, attempt count, and last activity. They never contain password hashes, tokens, quiz answers, or response details.
- Admin actions require a valid JWT whose current database user still has the admin role. Suspended students cannot log in or use student-only APIs.
- No admin action can promote a student, delete student history, or reveal a student's individual quiz answers.

## Data model

`lessons`: `course_id`, `topic_id`, `title`, `summary`, `content`, optional `video_url`, `position`, `published`, `created_at`, `updated_at`.

Lesson completion remains a separate per-student record keyed by `student_id` and `lesson_id`; this keeps curriculum content independent from learner activity.

Student account status is `active` (default for existing accounts) or `suspended`. Existing records remain intact when suspended.

## API design

- `GET /api/admin/lessons` and `POST /api/admin/lessons`
- `PUT /api/admin/lessons/:id` and `DELETE /api/admin/lessons/:id`
- `GET /api/courses/:course_id/lessons` returns published lessons to students and all lessons to admins.
- `GET /api/admin/students` returns a bounded, searchable list with aggregate activity only.
- `PATCH /api/admin/students/:id/status` accepts only `active` or `suspended`.
- Existing lesson completion API validates that the lesson exists and is published before recording completion.

## UI design

- Admin sidebar gains **Lessons** and **Students** pages.
- Lessons page provides a searchable table, course/topic mapping, draft/published state, and an editor for lesson text and optional YouTube URL.
- Students page provides search, profile/aggregate activity, and suspend/reactivate controls with clear confirmation.
- Student course details show published lessons under their matching topics, with a read lesson view and completion action.

## Delivery and acceptance

1. Implement and document API/data/security behavior.
2. Build admin lesson and student pages and forms.
3. Connect published lesson reading and completion to student course pages.
4. Review authorization, data exposure, escaping, and mobile layout.

Acceptance: admins can CRUD lessons and change student status; students can see only published lessons and cannot call admin APIs; suspended students cannot sign in; lesson completion is stored per student; dashboard progress counts real lesson completions; existing quiz/course workflows remain intact.

## Boundaries

This is a lightweight content/admin MVP. It does not include bulk imports, role promotion, account deletion, file uploads, rich text, or direct access to identifiable historical CSV records. Video URLs are optional and validated as HTTP(S); the UI may continue to offer topic-matched YouTube search links.
