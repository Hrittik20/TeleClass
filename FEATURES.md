# Feature Documentation

Complete list of features in Noētica LMS with usage examples.

## 📚 Core Features

### 1. Class Management

#### Create a Class
```
Method: Link Telegram group
Command: /init_class (in group)
API: POST /api/classes/link

Result: Class created with unique course code
```

**Features:**
- ✅ Link any Telegram group as a class
- ✅ Automatic course code generation
- ✅ Multiple classes per teacher
- ✅ Unlimited students per class

**Use Cases:**
- Different subjects (Math, Science, History)
- Different grades (Grade 9, Grade 10)
- Different cohorts (Fall 2024, Spring 2025)

---

### 2. Assignment System

#### Create Assignment
```
Method: Mini App Dashboard
Steps:
  1. Open /dashboard
  2. Click "New Assignment"
  3. Fill form
  4. Click "Create & Post"

Result: Assignment posted to group and pinned
```

**Features:**
- ✅ Markdown formatting for instructions
- ✅ Optional due dates
- ✅ Automatic posting to group
- ✅ Auto-pinning (if bot has permission)
- ✅ Edit after creation
- ✅ Close assignment to prevent late submissions

**Assignment Fields:**
- Title (required)
- Instructions (markdown supported)
- Due date (optional, ISO 8601 format)
- Status (open/closed)

**Example Assignment:**
```markdown
Title: Essay on Climate Change

Instructions:
## Requirements
- 500-700 words
- Use at least 3 sources
- Include citations

**Due:** December 31, 2024
**Format:** PDF or DOCX
```

#### Submit Assignment (Student)

**Method 1: Reply in Group**
```
1. Find assignment message in group
2. Reply to it with your file/text
3. Bot automatically captures submission
4. Receive confirmation
```

**Method 2: Mini App**
```
1. Open /dashboard
2. Find assignment
3. Click to open
4. Fill text field
5. Attach file (optional)
6. Click "Submit"
```

**Supported File Types:**
- Documents: PDF, DOC, DOCX, TXT
- Images: JPG, PNG, GIF
- Videos: MP4, MOV
- Archives: ZIP, RAR
- Code: PY, JS, HTML, etc.

#### View Submissions (Teacher)
```
Method: Mini App Dashboard
Steps:
  1. Open /dashboard
  2. Click on assignment
  3. View "Submissions" section

Shows:
  - Student name
  - Submission time
  - Late/On-time status
  - Text content
  - Attached files
```

#### Export Submissions
```
Method: Mini App Dashboard
Steps:
  1. Open assignment
  2. Click "Export CSV"

Result: CSV file with all submissions
Columns: student_id, student_name, timestamp, late, text, file_path
```

---

### 3. Quiz System

#### Create Quiz
```
API: POST /api/quiz/teacher/quizzes

Body:
{
  "class_id": "your_class_id",
  "title": "Chapter 1 Quiz",
  "description": "Test your understanding",
  "time_limit_minutes": 30,
  "due_at": "2024-12-31T23:59:59Z",
  "passing_score": 70
}
```

**Quiz Settings:**
- Title and description
- Time limit (optional)
- Due date (optional)
- Passing score (percentage)
- Status: draft → published → closed

#### Add Questions

**Question Types:**

**1. Multiple Choice**
```json
{
  "question_text": "What is the capital of France?",
  "question_type": "multiple_choice",
  "options": [
    {"id": "a", "text": "London"},
    {"id": "b", "text": "Paris"},
    {"id": "c", "text": "Berlin"},
    {"id": "d", "text": "Madrid"}
  ],
  "correct_answer": "b",
  "points": 1
}
```

**2. True/False**
```json
{
  "question_text": "The Earth is flat.",
  "question_type": "true_false",
  "correct_answer": false,
  "points": 1
}
```

**3. Short Answer**
```json
{
  "question_text": "What is H2O?",
  "question_type": "short_answer",
  "correct_answer": "water",
  "points": 2
}
```
*Note: Case-insensitive matching*

**4. Essay**
```json
{
  "question_text": "Explain the water cycle in detail.",
  "question_type": "essay",
  "points": 5
}
```
*Note: Requires manual grading*

#### Take Quiz (Student)
```
Method: Mini App Dashboard
Steps:
  1. Open /dashboard
  2. Navigate to "Quizzes"
  3. Click on quiz
  4. Click "Start Quiz"
  5. Answer all questions
  6. Click "Submit"

Result: Instant score for objective questions
```

**Quiz Taking Features:**
- ✅ Timer countdown
- ✅ Save answers as you go
- ✅ Review before submit
- ✅ Instant results for objective questions
- ✅ See correct answers after completion
- ✅ Multiple attempts (if allowed)

#### View Quiz Results (Teacher)
```
Method: Mini App Dashboard
Steps:
  1. Open quiz
  2. View "Students" section

Shows:
  - Student name
  - Number of attempts
  - Best score
  - Individual attempt details
```

---

### 4. Student Enrollment

#### Enroll in Course
```
Method: Mini App Dashboard
Steps:
  1. Open /dashboard
  2. Click "Enroll in Course"
  3. Enter course code (from teacher)
  4. Click "Enroll"

Result: Access to all course assignments and quizzes
```

**Course Code:**
- 8-character alphanumeric code
- Generated automatically when class is created
- Share with students via any method
- One code per class

**Example:**
```
Teacher creates class → Gets code: ABC123XY
Teacher shares code with students
Students enter code in Mini App
Students can now see all course content
```

---

### 5. Progress Tracking

#### Student Dashboard
```
View: Mini App → Progress Tab

Shows:
  - Total assignments
  - Completed assignments
  - Pending assignments
  - Late assignments
  - Completion percentage
  - Course-wise progress
```

**Metrics:**
- 📊 Completion rate (%)
- ⏱️ Average submission time
- 🎯 Quiz scores
- 📈 Progress trend

#### Teacher Dashboard
```
View: Mini App → Class Overview

Shows:
  - Total students enrolled
  - Total assignments posted
  - Submission rate
  - Average scores
  - Pending grading
```

---

### 6. File Management

#### Upload Files
```
Max size: Configurable (default: no limit)
Supported: Any file type
Storage: Local filesystem or cloud
```

**File Handling:**
1. Student uploads file
2. Server generates unique ID
3. File saved to `data/files/`
4. Metadata stored in database
5. Teacher can download via API

**File Metadata:**
```json
{
  "file_id": "uuid-here",
  "filename": "homework.pdf",
  "mime_type": "application/pdf",
  "size": 12345,
  "local_path": "/path/to/file"
}
```

#### Download Files
```
API: GET /api/files/{file_id}
Result: File download with original filename
```

---

### 7. Notifications

#### Teacher Notifications
```
Trigger: New submission
Method: Telegram DM
Content: Student name, assignment, timestamp
```

#### Student Notifications
```
Trigger: Assignment posted
Method: Group message
Content: Assignment details, due date, instructions
```

#### Reminders
```
Method: Mini App Dashboard
Steps:
  1. Open assignment
  2. Click "Send Reminder"

Result: Reminder sent to group
```

---

### 8. Bot Commands

#### Available Commands

**For Everyone:**
```
/start - Welcome message and introduction
/dashboard - Open the Mini App dashboard
```

**For Teachers (in groups):**
```
/init_class - Link this group as a class
```

**Command Examples:**

```bash
# Student workflow
1. /start → See welcome message
2. /dashboard → Open Mini App
3. Enroll in course
4. View assignments
5. Submit work

# Teacher workflow
1. Create group
2. Add bot to group
3. /init_class in group
4. /dashboard in private chat
5. Create assignments
```

---

### 9. Search and Filters

#### Student: Assignment Search
```
View: Mini App → Assignments Tab
Features:
  - Search by title
  - Filter by course
  - Filter by status (pending/submitted)
  - Sort by due date
```

#### Teacher: Submission Filters
```
View: Mini App → Assignment Details
Features:
  - Filter by submission status
  - Filter by late/on-time
  - Sort by name or date
```

---

### 10. Data Export

#### Export Submissions to CSV
```
Method: Mini App Dashboard
Result: CSV file with columns:
  - submission_id
  - student_tg_id
  - student_name
  - timestamp
  - late (true/false)
  - has_file (true/false)
  - file_path
  - text_content
```

**Use Cases:**
- Grade book import
- Data analysis
- Record keeping
- Backup

---

## 🔧 Advanced Features

### 1. Reply-Based Submissions

**How it works:**
```
1. Bot posts assignment to group
2. Student replies to that specific message
3. Bot detects reply using message_id
4. Bot extracts file/text from reply
5. Bot saves as submission
6. Bot confirms to student
```

**Advantages:**
- No need to leave Telegram
- Natural workflow for users
- Works on mobile perfectly
- No Mini App required

**Limitations:**
- Must reply to correct message
- Bot needs privacy mode disabled
- Can't edit after submission

---

### 2. Markdown Support

**In Assignments:**
```markdown
# Main Title
## Subtitles

**Bold text**
*Italic text*

- Bullet points
1. Numbered lists

[Links](https://example.com)

`code snippets`
```

**Rendering:**
- In Telegram: Basic markdown
- In Mini App: Full HTML rendering

---

### 3. Role-Based Access

**Roles:**
- Teacher: Can create/manage content
- Student: Can view/submit
- Both: User can be both roles

**Permissions:**
```
Teacher can:
  ✅ Create classes
  ✅ Create assignments
  ✅ Create quizzes
  ✅ View all submissions
  ✅ Export data
  ✅ Send reminders

Student can:
  ✅ Enroll in courses
  ✅ View assignments
  ✅ Submit work
  ✅ Take quizzes
  ✅ View own progress

Student cannot:
  ❌ See other students' submissions
  ❌ Create assignments
  ❌ Modify grading
  ❌ Access teacher dashboard
```

---

### 4. Automatic Grading

**Graded Automatically:**
- Multiple choice questions
- True/false questions
- Short answer (exact match)

**Requires Manual Grading:**
- Essay questions
- File submissions
- Complex assignments

**Grading Process:**
```
1. Student completes quiz
2. Click "Submit"
3. Server compares answers
4. Calculate score
5. Return results immediately
6. Store attempt in database
```

**Scoring:**
```
Score = (Points Earned / Total Points) × 100
Example: (8 / 10) × 100 = 80%
```

---

### 5. Audit Logging

**All actions logged:**
```json
{
  "id": "E123456789",
  "type": "assignment_created",
  "actor": 123456,
  "payload": {
    "assignment_id": "A123456",
    "title": "Homework 1"
  },
  "timestamp": "2024-01-01T00:00:00Z"
}
```

**Event Types:**
- teacher_created
- student_created
- class_linked
- assignment_created
- assignment_updated
- submission_added
- quiz_created
- quiz_attempt_started
- quiz_attempt_completed
- student_enrolled

**Use Cases:**
- Debugging
- Analytics
- Compliance
- User activity tracking

---

## 🎯 Use Case Examples

### Example 1: Weekly Homework

```
Teacher:
1. Create assignment "Week 1 Homework"
2. Set due date: Friday 11:59 PM
3. Post to group

Students (throughout week):
- Reply to message with completed work
- Or submit via Mini App

Friday 11:59 PM:
- Submissions close automatically

Teacher:
- Export all submissions
- Grade offline
- Record in grade book
```

### Example 2: Pop Quiz

```
Teacher:
1. Create quiz with 10 questions
2. Set time limit: 15 minutes
3. Publish immediately
4. Announce in group

Students (next 24 hours):
- Take quiz when ready
- Get instant results
- See correct answers

Teacher:
- View results dashboard
- Identify struggling students
- Offer additional help
```

### Example 3: Project Submission

```
Teacher:
1. Create assignment "Final Project"
2. No due date (ongoing)
3. Detailed instructions in markdown
4. Post to group

Students (over several weeks):
- Work on project
- Ask questions in group
- Submit when ready
- Can resubmit if allowed

Teacher:
- View submissions as they come
- Download files
- Grade individually
- Provide feedback
```

---

## 📊 Limitations & Constraints

### Current Limitations

**Storage:**
- ❌ No pagination (all data loaded)
- ❌ No search indexes
- ❌ File size not validated
- ❌ Limited to single JSON file

**Features:**
- ❌ No grading interface (yet)
- ❌ No discussion forums
- ❌ No video content
- ❌ No calendar view
- ❌ No parent portal

**Scale:**
- ❌ Optimal for <100 users
- ❌ May slow down with >1000 submissions
- ❌ Single server only

### Planned Improvements

**Phase 1:**
- [ ] Add pagination
- [ ] Implement search
- [ ] Add file validation
- [ ] Grading interface

**Phase 2:**
- [ ] PostgreSQL migration
- [ ] Real-time updates
- [ ] Discussion forums
- [ ] Rich media support

**Phase 3:**
- [ ] Multi-server deployment
- [ ] Advanced analytics
- [ ] Integration APIs
- [ ] Mobile apps

---

## 🔒 Security Features

**Implemented:**
- ✅ Telegram WebApp auth validation
- ✅ Role-based access control
- ✅ User ID verification
- ✅ CORS protection
- ✅ Atomic database writes

**Recommended for Production:**
- [ ] Rate limiting
- [ ] File type validation
- [ ] File size limits
- [ ] Malware scanning
- [ ] SQL injection prevention (N/A with JSON)
- [ ] XSS protection
- [ ] CSRF tokens
- [ ] Input sanitization

---

## 📚 API Rate Limits

**Current:** No rate limits

**Recommended for Production:**
```python
- 100 requests/minute per user
- 1000 requests/hour per user
- 10 file uploads/hour per user
- 5 quiz attempts/day per student
```

---

## 🌐 Internationalization

**Current:** English only

**Future:**
- [ ] Multi-language support
- [ ] RTL language support
- [ ] Date/time localization
- [ ] Number formatting

---

For implementation details, see [API_REFERENCE.md](API_REFERENCE.md)

For architecture, see [ARCHITECTURE.md](ARCHITECTURE.md)

