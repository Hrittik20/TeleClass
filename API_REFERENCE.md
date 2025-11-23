# API Reference

Complete API documentation for Noētica LMS.

## Base URL

```
http://localhost:8000
```

## Authentication

All endpoints require Telegram WebApp authentication via the `X-Telegram-Init-Data` header.

For development, you can use:
- Header: `x-dev-user-id: <telegram_user_id>`
- Set `DEV_SKIP_INITDATA_VALIDATION=true` in `.env`

## Common Endpoints

### Health Check

```http
GET /api/health
```

**Response:**
```json
{
  "ok": true
}
```

### Verify Authentication

```http
POST /api/auth/verify
```

**Response:**
```json
{
  "authenticated": true,
  "user_id": 123456,
  "is_teacher": true,
  "is_student": false,
  "teacher": {
    "tg_user_id": 123456,
    "name": "John Doe",
    "created_at": "2024-01-01T00:00:00Z"
  },
  "student": null
}
```

---

## Teacher Endpoints

### Link Class

Create or link a Telegram group as a class.

```http
POST /api/classes/link
```

**Request Body:**
```json
{
  "group_chat_id": -1001234567890,
  "group_title": "Physics 101"
}
```

**Response:**
```json
{
  "class_id": "-1001234567890",
  "title": "Physics 101",
  "teacher_tg_id": 123456,
  "course_code": "ABC123XY",
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Create Assignment

Create and post an assignment to a group.

```http
POST /api/assignments
```

**Request Body:**
```json
{
  "class_id": "-1001234567890",
  "title": "Chapter 1 Homework",
  "instructions_md": "Read chapter 1 and answer questions 1-10",
  "due_at": "2024-12-31T23:59:59Z"
}
```

**Response:**
```json
{
  "assignment_id": "A1234567890",
  "class_id": "-1001234567890",
  "title": "Chapter 1 Homework",
  "instructions_md": "Read chapter 1 and answer questions 1-10",
  "due_at": "2024-12-31T23:59:59Z",
  "posted_message_id": 123,
  "status": "open",
  "created_at": "2024-01-01T00:00:00Z"
}
```

### List Assignments

Get all assignments for a class.

```http
GET /api/assignments?class_id=-1001234567890
```

**Response:**
```json
[
  {
    "assignment_id": "A1234567890",
    "class_id": "-1001234567890",
    "title": "Chapter 1 Homework",
    "instructions_md": "Read chapter 1 and answer questions 1-10",
    "due_at": "2024-12-31T23:59:59Z",
    "posted_message_id": 123,
    "status": "open",
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

### Update Assignment

Modify an existing assignment.

```http
PATCH /api/assignments/{assignment_id}
```

**Request Body:**
```json
{
  "title": "Updated Title",
  "instructions_md": "Updated instructions",
  "due_at": "2024-12-31T23:59:59Z",
  "status": "closed"
}
```

**Response:**
```json
{
  "assignment_id": "A1234567890",
  "class_id": "-1001234567890",
  "title": "Updated Title",
  "instructions_md": "Updated instructions",
  "due_at": "2024-12-31T23:59:59Z",
  "status": "closed",
  "updated_at": "2024-01-02T00:00:00Z"
}
```

### View Submissions

Get all submissions for an assignment.

```http
GET /api/assignments/{assignment_id}/submissions
```

**Response:**
```json
[
  {
    "submission_id": "S1234567890",
    "assignment_id": "A1234567890",
    "student_tg_id": 789012,
    "student_name": "Jane Smith",
    "text": "Here is my answer...",
    "file": {
      "file_id": "uuid",
      "filename": "homework.pdf",
      "mime": "application/pdf",
      "size": 12345,
      "local_path": "/path/to/file"
    },
    "ts": "2024-01-15T12:00:00Z",
    "late": false
  }
]
```

### Send Reminder

Send a reminder about an assignment to the group.

```http
POST /api/assignments/{assignment_id}/remind
```

**Response:**
```json
{
  "ok": true
}
```

### Export Submissions to CSV

Export all submissions for an assignment.

```http
POST /api/assignments/{assignment_id}/export_csv
```

**Response:**
```json
{
  "csv_path": "/path/to/export_A1234567890.csv"
}
```

---

## Student Endpoints

### List Enrolled Courses

Get all courses the student is enrolled in.

```http
GET /api/student/courses
```

**Response:**
```json
{
  "courses": [
    {
      "id": "-1001234567890",
      "title": "Physics 101",
      "teacher_name": "Dr. Johnson",
      "assignment_count": 5,
      "completed_count": 3
    }
  ]
}
```

### Enroll in Course

Enroll in a course using a course code.

```http
POST /api/student/enroll
```

**Request Body:**
```json
{
  "course_code": "ABC123XY"
}
```

**Response:**
```json
{
  "success": true,
  "course_id": "-1001234567890"
}
```

### List Assignments

Get all assignments from enrolled courses.

```http
GET /api/student/assignments
```

**Response:**
```json
{
  "assignments": [
    {
      "id": "A1234567890",
      "title": "Chapter 1 Homework",
      "instructions": "Read chapter 1 and answer questions 1-10",
      "course_id": "-1001234567890",
      "course_title": "Physics 101",
      "due_at": "2024-12-31T23:59:59Z",
      "closed": false,
      "submitted": true
    }
  ]
}
```

### Get Assignment Details

Get detailed information about a specific assignment.

```http
GET /api/student/assignments/{assignment_id}
```

**Response:**
```json
{
  "assignment": {
    "id": "A1234567890",
    "title": "Chapter 1 Homework",
    "instructions": "Read chapter 1 and answer questions 1-10",
    "course_id": "-1001234567890",
    "course_title": "Physics 101",
    "due_at": "2024-12-31T23:59:59Z",
    "closed": false,
    "submission": {
      "id": "S1234567890",
      "submitted_at": "2024-01-15T12:00:00Z",
      "text": "Here is my answer...",
      "files": [
        {
          "name": "homework.pdf",
          "url": "/api/files/uuid",
          "mime_type": "application/pdf",
          "size": 12345
        }
      ],
      "status": "on_time"
    }
  }
}
```

### Submit Assignment

Submit an assignment with text and/or file.

```http
POST /api/student/assignments/{assignment_id}/submit
```

**Request Body (multipart/form-data):**
- `text`: string (optional)
- `file`: file (optional)

**Response:**
```json
{
  "success": true,
  "submission_id": "S1234567890"
}
```

**Example with curl:**
```bash
curl -X POST "http://localhost:8000/api/student/assignments/A1234567890/submit" \
  -H "x-dev-user-id: 789012" \
  -F "text=Here is my answer" \
  -F "file=@homework.pdf"
```

---

## Quiz Endpoints

### Teacher: Create Quiz

```http
POST /api/quiz/teacher/quizzes
```

**Request Body:**
```json
{
  "class_id": "-1001234567890",
  "title": "Chapter 1 Quiz",
  "description": "Test your understanding of chapter 1",
  "time_limit_minutes": 30,
  "due_at": "2024-12-31T23:59:59Z",
  "passing_score": 70
}
```

**Response:**
```json
{
  "quiz_id": "Q1234567890",
  "class_id": "-1001234567890",
  "title": "Chapter 1 Quiz",
  "description": "Test your understanding of chapter 1",
  "time_limit_minutes": 30,
  "due_at": "2024-12-31T23:59:59Z",
  "passing_score": 70,
  "status": "draft",
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Teacher: List Quizzes

```http
GET /api/quiz/teacher/quizzes?class_id=-1001234567890
```

**Response:**
```json
{
  "quizzes": [
    {
      "quiz_id": "Q1234567890",
      "title": "Chapter 1 Quiz",
      "status": "published",
      "question_count": 5,
      "attempt_count": 10
    }
  ]
}
```

### Teacher: Add Question

```http
POST /api/quiz/teacher/questions
```

**Request Body:**
```json
{
  "quiz_id": "Q1234567890",
  "question_text": "What is 2 + 2?",
  "question_type": "multiple_choice",
  "options": [
    {"id": "a", "text": "3"},
    {"id": "b", "text": "4"},
    {"id": "c", "text": "5"},
    {"id": "d", "text": "6"}
  ],
  "correct_answer": "b",
  "points": 1
}
```

**Question Types:**
- `multiple_choice`: Select one option
- `true_false`: Boolean answer
- `short_answer`: Text input
- `essay`: Long text (requires manual grading)

**Response:**
```json
{
  "question_id": "QQ1234567890",
  "quiz_id": "Q1234567890",
  "question_text": "What is 2 + 2?",
  "question_type": "multiple_choice",
  "options": [...],
  "correct_answer": "b",
  "points": 1
}
```

### Teacher: Publish Quiz

```http
PATCH /api/quiz/teacher/quizzes/{quiz_id}
```

**Request Body:**
```json
{
  "status": "published"
}
```

### Student: List Available Quizzes

```http
GET /api/quiz/student/quizzes
```

**Response:**
```json
{
  "quizzes": [
    {
      "quiz_id": "Q1234567890",
      "title": "Chapter 1 Quiz",
      "description": "Test your understanding",
      "course_id": "-1001234567890",
      "course_title": "Physics 101",
      "due_at": "2024-12-31T23:59:59Z",
      "time_limit_minutes": 30,
      "attempt_count": 1,
      "best_score": 85,
      "passing_score": 70
    }
  ]
}
```

### Student: Start Quiz Attempt

```http
POST /api/quiz/student/attempts
```

**Request Body:**
```json
{
  "quiz_id": "Q1234567890"
}
```

**Response:**
```json
{
  "attempt": {
    "attempt_id": "QA1234567890",
    "quiz_id": "Q1234567890",
    "student_tg_id": 789012,
    "start_time": "2024-01-15T12:00:00Z",
    "status": "in_progress"
  },
  "questions": [
    {
      "question_id": "QQ1234567890",
      "question_text": "What is 2 + 2?",
      "question_type": "multiple_choice",
      "options": [...],
      "points": 1
    }
  ]
}
```

### Student: Answer Question

```http
POST /api/quiz/student/attempts/{attempt_id}/answer
```

**Request Body:**
```json
{
  "question_id": "QQ1234567890",
  "answer": "b"
}
```

**Response:**
```json
{
  "attempt_id": "QA1234567890",
  "answers": {
    "QQ1234567890": "b"
  },
  "status": "in_progress"
}
```

### Student: Complete Quiz

```http
POST /api/quiz/student/attempts/{attempt_id}/complete
```

**Response:**
```json
{
  "attempt": {
    "attempt_id": "QA1234567890",
    "quiz_id": "Q1234567890",
    "score": 85,
    "status": "completed",
    "end_time": "2024-01-15T12:30:00Z"
  },
  "passed": true
}
```

---

## File Access

### Get File

Download a submitted file.

```http
GET /api/files/{file_id}
```

**Response:** File download

---

## Error Responses

All endpoints return errors in this format:

```json
{
  "detail": "Error message here"
}
```

### Common Error Codes

- `400` - Bad Request (invalid input)
- `401` - Unauthorized (authentication failed)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found (resource doesn't exist)
- `500` - Internal Server Error

---

## Rate Limiting

Currently no rate limiting is implemented. Consider adding rate limiting in production.

## CORS

CORS is enabled for all origins in development. Configure appropriately for production.

## WebSocket Support

Not currently implemented. Future versions may include real-time updates via WebSockets.

---

For more information, visit the [FastAPI docs](http://localhost:8000/docs) when the server is running.

