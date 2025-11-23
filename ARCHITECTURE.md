# System Architecture

Technical overview of the Noētica LMS architecture.

## Overview

Noētica LMS is built as a microservices-style application with three main components:

1. **Telegram Bot** - Handles user interactions via Telegram
2. **FastAPI Server** - REST API for data management
3. **Mini App** - Web-based UI served within Telegram

```
┌─────────────────────────────────────────────────────────┐
│                     Telegram Platform                    │
│  ┌────────────┐  ┌────────────┐  ┌─────────────────┐   │
│  │   Users    │  │    Bot     │  │   Mini Apps     │   │
│  └─────┬──────┘  └──────┬─────┘  └────────┬────────┘   │
└────────┼─────────────────┼─────────────────┼────────────┘
         │                 │                 │
         │                 │                 │ HTTPS
         │                 │                 │
         │          ┌──────▼─────────────────▼──────┐
         │          │     FastAPI Server             │
         │          │  ┌──────────────────────────┐  │
         │          │  │   Authentication Layer   │  │
         │          │  └──────────────────────────┘  │
         │          │  ┌──────────────────────────┐  │
         │          │  │    API Endpoints         │  │
         │          │  │  • Teacher APIs          │  │
         │          │  │  • Student APIs          │  │
         │          │  │  • Quiz APIs             │  │
         │          │  └──────────────────────────┘  │
         │          │  ┌──────────────────────────┐  │
         │          │  │  Telegram API Client     │  │
         │          │  └──────────────────────────┘  │
         │          └────────────┬──────────────────┘
         │                       │
    ┌────▼────────┐         ┌───▼────────┐
    │ Telegram    │         │  Storage   │
    │ Bot Process │         │  (JSON DB) │
    └─────────────┘         └────────────┘
```

## Components

### 1. Telegram Bot (`bot/bot.py`)

**Purpose:** Handle direct Telegram interactions

**Responsibilities:**
- Process bot commands (`/start`, `/dashboard`, `/init_class`)
- Capture reply-based submissions
- Send notifications to users
- Manage group interactions

**Key Features:**
- Long polling for real-time updates
- Reply detection for assignment submissions
- Automatic file handling
- Message pinning

**Technology:**
- `python-telegram-bot` library
- Async/await for concurrent operations

**Flow:**
```
User Message → Bot Handler → Storage → Telegram API Response
                    ↓
              (Optional) API Call to Server
```

### 2. FastAPI Server (`server/app.py`)

**Purpose:** Provide REST API for data operations

**Responsibilities:**
- Handle CRUD operations for classes, assignments, quizzes
- Authenticate Telegram users
- Serve static files (Mini App)
- Manage file uploads
- Export data

**Modules:**
- `app.py` - Main server, teacher endpoints
- `student_api.py` - Student-specific endpoints
- `quiz_api.py` - Quiz and question management
- `telegram_api.py` - Helper functions for Telegram API calls

**Technology:**
- FastAPI web framework
- Uvicorn ASGI server
- Pydantic for data validation

**Middleware:**
- CORS for cross-origin requests
- Static file serving

**Authentication Flow:**
```
Mini App → initData → Server Validation → User ID → Database
```

### 3. Storage Layer (`storage/`)

**Purpose:** Data persistence and management

**Implementation:** File-based JSON database with atomic writes

**Modules:**
- `storage.py` - Core storage functions
- `quiz.py` - Quiz-specific storage

**Data Structure:**
```json
{
  "meta": {},
  "teachers": {},
  "students": {},
  "classes": {},
  "assignments": {},
  "submissions": {},
  "enrollments": {},
  "quizzes": {},
  "questions": {},
  "quiz_attempts": {},
  "events": []
}
```

**Key Features:**
- Thread-safe with locks
- Atomic writes using temp files
- Audit log (events array)
- Automatic directory creation

**Why JSON?**
- Zero setup required
- Easy to inspect and debug
- Portable across systems
- Sufficient for small to medium deployments
- Easy migration to database later

### 4. Mini App Frontend (`frontend/`, `miniapp/`)

**Purpose:** Web-based UI within Telegram

**Components:**
- `miniapp/index.html` - Entry point with role selection
- `frontend/teacher.html` - Teacher dashboard
- `frontend/student.html` - Student dashboard

**Technology:**
- Pure HTML/CSS/JavaScript (no build step)
- Tailwind CSS via CDN
- Telegram WebApp SDK

**Features:**
- Responsive design
- Dark/light theme support (Telegram theme)
- Real-time updates via API polling
- File upload with drag & drop

## Data Flow

### Assignment Creation Flow

```
1. Teacher opens Mini App
2. Click "Create Assignment"
3. Fill form and submit
   ↓
4. POST /api/assignments
   ↓
5. Server validates teacher owns class
   ↓
6. Server creates assignment in storage
   ↓
7. Server calls Telegram API to post message
   ↓
8. Server updates assignment with message_id
   ↓
9. Server responds to Mini App
   ↓
10. Mini App refreshes assignment list
```

### Reply-Based Submission Flow

```
1. Student replies to assignment message in group
   ↓
2. Bot receives message via polling
   ↓
3. Bot checks if reply is to a known assignment
   ↓
4. Bot extracts file/text from message
   ↓
5. Bot saves submission to storage
   ↓
6. Bot confirms to student
   ↓
7. Bot notifies teacher via DM
```

### Quiz Taking Flow

```
1. Student opens quiz in Mini App
   ↓
2. POST /api/quiz/student/attempts
   ↓
3. Server creates attempt record
   ↓
4. Server returns questions (without correct answers)
   ↓
5. Student answers each question
   ↓
6. POST /api/quiz/student/attempts/{id}/answer (for each)
   ↓
7. Student clicks "Submit"
   ↓
8. POST /api/quiz/student/attempts/{id}/complete
   ↓
9. Server calculates score
   ↓
10. Server returns results with correct answers
```

## Security Architecture

### Authentication

**Telegram WebApp initData:**
- Contains signed user data from Telegram
- Includes hash for verification
- Short-lived (expires after a few minutes)

**Validation Process:**
```python
1. Extract initData from request header
2. Parse query string
3. Extract hash from data
4. Compute HMAC-SHA256 with bot token
5. Compare hashes
6. If valid, extract user_id
7. Use user_id for authorization
```

**Development Mode:**
- `DEV_SKIP_INITDATA_VALIDATION=true` bypasses validation
- Use `x-dev-user-id` header for testing
- **Never use in production!**

### Authorization

**Role-Based Access Control (RBAC):**
- Teachers can only access their own classes
- Students can only access enrolled courses
- Assignment submissions checked against enrollment

**Ownership Checks:**
```python
# Example from code
cls = storage.get_class(class_id)
if cls["teacher_tg_id"] != user_id:
    raise HTTPException(403, "Not your class")
```

### File Upload Security

**Current Implementation:**
- Files saved to `data/files/` directory
- Unique UUID-based filenames
- No size limit (should add in production)
- No file type validation (should add in production)

**Recommendations for Production:**
- Limit file sizes (e.g., 10MB max)
- Validate file types (check MIME and extension)
- Scan for malware
- Use cloud storage (S3, Google Cloud Storage)
- Generate signed URLs for access

## Scalability Considerations

### Current Limitations

1. **Single JSON File:**
   - Lock contention with many concurrent writes
   - File size grows unbounded
   - No query optimization

2. **In-Memory Processing:**
   - All data loaded on each operation
   - No caching layer
   - No pagination

3. **Single Process:**
   - Bot and API run separately
   - No load balancing
   - Limited concurrent request handling

### Migration Path

**Phase 1: File-based (Current)**
- Perfect for <100 users
- <10 classes
- Development and testing

**Phase 2: SQLite**
```python
# Replace JSON with SQLite
# Pro: SQL queries, indexes, better concurrency
# Con: Still single file, limited scalability
```

**Phase 3: PostgreSQL/MySQL**
```python
# Full RDBMS
# Pro: Unlimited scale, replication, backups
# Con: More complex setup and maintenance
```

**Phase 4: Microservices + Cache**
```
┌─────────┐    ┌─────────┐    ┌──────────┐
│   Bot   │───▶│  Redis  │◀───│   API    │
└─────────┘    └─────────┘    └──────────┘
                     │              │
                     └──────┬───────┘
                            │
                     ┌──────▼──────┐
                     │  PostgreSQL │
                     └─────────────┘
```

## Deployment Architecture

### Development

```
┌──────────────┐
│   Localhost  │
│  ┌────────┐  │
│  │  Bot   │  │
│  └────────┘  │
│  ┌────────┐  │
│  │  API   │  │
│  └────────┘  │
└──────────────┘
      │
      │ ngrok tunnel
      │
┌─────▼────────┐
│   Telegram   │
└──────────────┘
```

### Production (Simple)

```
┌───────────────────────┐
│   Cloud Server        │
│  ┌────────────────┐   │
│  │  Systemd       │   │
│  │  ┌──────────┐  │   │
│  │  │   Bot    │  │   │
│  │  └──────────┘  │   │
│  │  ┌──────────┐  │   │
│  │  │   API    │  │   │
│  │  └──────────┘  │   │
│  └────────────────┘   │
│  ┌────────────────┐   │
│  │   Nginx        │   │
│  │   (SSL/TLS)    │   │
│  └────────────────┘   │
└───────────────────────┘
         │
         │ HTTPS
         │
┌────────▼──────────┐
│    Telegram       │
└───────────────────┘
```

### Production (Docker)

```
┌───────────────────────────────┐
│   Docker Host                 │
│  ┌─────────────────────────┐  │
│  │  docker-compose         │  │
│  │  ┌────────┐ ┌────────┐  │  │
│  │  │  Bot   │ │  API   │  │  │
│  │  │ Container Container│  │  │
│  │  └────────┘ └────────┘  │  │
│  │       │          │       │  │
│  │       └────┬─────┘       │  │
│  │            │             │  │
│  │     ┌──────▼──────┐      │  │
│  │     │   Volume    │      │  │
│  │     │   (data/)   │      │  │
│  │     └─────────────┘      │  │
│  └─────────────────────────┘  │
└───────────────────────────────┘
```

### Production (Kubernetes)

```
┌──────────────────────────────────────┐
│   Kubernetes Cluster                 │
│  ┌────────────────────────────────┐  │
│  │  Deployment: Bot (3 replicas)  │  │
│  └────────────────────────────────┘  │
│  ┌────────────────────────────────┐  │
│  │  Deployment: API (5 replicas)  │  │
│  └────────────────────────────────┘  │
│  ┌────────────────────────────────┐  │
│  │  Service: Load Balancer        │  │
│  └────────────────────────────────┘  │
│  ┌────────────────────────────────┐  │
│  │  PersistentVolume: Database    │  │
│  └────────────────────────────────┘  │
│  ┌────────────────────────────────┐  │
│  │  Ingress: SSL Termination      │  │
│  └────────────────────────────────┘  │
└──────────────────────────────────────┘
```

## Monitoring and Logging

### Current State

**Logging:**
- Console output only
- Basic error messages
- No log rotation

**Monitoring:**
- None

### Recommended Additions

```python
# Add structured logging
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

# Add metrics
from prometheus_client import Counter, Histogram
assignment_submissions = Counter('submissions_total', 'Total submissions')
api_latency = Histogram('api_request_duration_seconds', 'API latency')

# Add health checks
@app.get("/health")
def health():
    return {
        "status": "healthy",
        "uptime": get_uptime(),
        "database": check_database(),
        "telegram": check_telegram_api()
    }
```

## Performance Optimization

### Current Bottlenecks

1. **File I/O:** Every operation reads/writes entire JSON file
2. **No Caching:** Same data fetched repeatedly
3. **No Indexing:** Linear search through arrays
4. **Synchronous Operations:** Limited concurrency

### Optimization Strategies

**Short Term:**
- Add in-memory cache for frequently accessed data
- Implement pagination for large lists
- Use async/await throughout
- Add database indexes

**Long Term:**
- Migrate to PostgreSQL
- Add Redis for caching and pub/sub
- Implement CDN for static files
- Use message queue for background tasks

## Testing Strategy

### Unit Tests
```python
# Test storage operations
def test_create_assignment():
    assignment = storage.create_assignment(
        "class_1", "Test", "Instructions", None
    )
    assert assignment["title"] == "Test"

# Test API endpoints
def test_assignment_creation_api():
    response = client.post("/api/assignments", json={...})
    assert response.status_code == 200
```

### Integration Tests
```python
# Test full flow
def test_assignment_submission_flow():
    # Create class
    # Create assignment
    # Submit as student
    # Verify teacher can see submission
```

### End-to-End Tests
```python
# Use Telegram Bot API test framework
# Simulate full user journey
```

## Future Enhancements

1. **Real-time Updates:** WebSocket support
2. **Rich Media:** Video lectures, interactive content
3. **Analytics:** Student progress tracking
4. **Gamification:** Badges, leaderboards
5. **Integrations:** Google Classroom, Canvas, Moodle
6. **Mobile Apps:** Native iOS/Android apps
7. **AI Features:** Auto-grading, recommendations
8. **Collaboration:** Group assignments, peer review

---

This architecture is designed to be simple and maintainable while providing room for growth. Start with the current file-based system and migrate to more robust solutions as your user base grows.

