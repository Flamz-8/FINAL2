# Implementation Plan: Student Knowledge Management App

**Branch**: `001-student-knowledge-app` | **Date**: 2025-11-23 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-student-knowledge-app/spec.md`

## Summary

Build a personal knowledge management app for students that centralizes class notes, study materials, and task management. Primary users are high school and college students who need to capture information quickly (during lectures), organize it by course, and see what needs to be done across all their classes. Technical approach uses Python 3.14+ with FastAPI backend, SQLite for local-first data storage, and a responsive web frontend, all initialized with `uv` for modern Python project management.

## Technical Context

**Language/Version**: Python 3.14+ (using latest stable Python >= 3.14)  
**Primary Dependencies**: FastAPI (REST API), SQLAlchemy (ORM), Pydantic (data validation), SQLite (database), pytest (testing), HTTPX (async HTTP client for tests)  
**Storage**: SQLite with local file storage (offline-first architecture, sync capability for future)  
**Testing**: pytest with pytest-asyncio, pytest-cov for coverage reporting  
**Target Platform**: Cross-platform web application (desktop and mobile browsers)
**Project Type**: Web application (FastAPI backend + HTML/CSS/JS frontend)  
**Performance Goals**: < 500ms note/task creation, < 100ms UI interactions, < 1s search for 1000 items, < 2s initial page load  
**Constraints**: < 200ms p95 API latency, < 200MB memory on desktop, < 100MB on mobile, offline-capable with sync queue  
**Scale/Scope**: Single-user focused, 50 courses max, 1000 notes max, 500 tasks max per student

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Code Quality Standards**:
- [x] Feature design supports single responsibility (models, services, API routes separated; each handles one entity)
- [x] Type safety strategy defined (Pydantic models for all DTOs, type hints on all functions, mypy for static checking)
- [x] Error handling approach documented (FastAPI exception handlers, structured error responses, logging with context)
- [x] Code review process confirmed (peer review required per constitution, PR template enforces checklist)

**Test-First Development**:
- [x] Test categories identified (contract tests for REST APIs, integration tests for user journeys, unit tests for business logic)
- [x] Coverage targets defined (100% for auth/date-filtering/note-task-linking, 90% for CRUD operations, 80% overall)
- [x] TDD workflow planned (pytest tests written first, run to fail, implement to pass, refactor with green tests)

**User Experience Consistency**:
- [x] Design system compliance confirmed (Tailwind CSS with custom spacing scale, color palette for courses/priorities/status)
- [x] Accessibility requirements defined (WCAG 2.1 Level AA: semantic HTML, ARIA labels, keyboard navigation, 4.5:1 contrast)
- [x] Error message strategy documented (user-friendly messages with next steps, technical details in logs)
- [x] Loading and feedback states specified (skeleton screens, spinners >500ms, optimistic UI updates, toast notifications)

**Performance Requirements**:
- [x] Latency targets defined (< 500ms saves, < 100ms interactions, < 200ms p95 APIs, < 1s search, < 2s page load)
- [x] Resource constraints identified (SQLite pagination, lazy loading, no blocking ops, response compression)
- [x] Scalability requirements documented (N+1 query prevention via eager loading, indexed queries for date filtering)
- [x] Performance monitoring plan (FastAPI middleware for timing, pytest benchmarks, memory profiling)

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── study_helper/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app entry point
│   │   ├── models/              # SQLAlchemy ORM models
│   │   │   ├── __init__.py
│   │   │   ├── base.py          # Base model class
│   │   │   ├── user.py          # User model
│   │   │   ├── course.py        # Course model
│   │   │   ├── note.py          # Note model
│   │   │   ├── task.py          # Task and Subtask models
│   │   │   └── tag.py           # Tag model
│   │   ├── schemas/             # Pydantic schemas (request/response DTOs)
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── course.py
│   │   │   ├── note.py
│   │   │   ├── task.py
│   │   │   └── common.py        # Shared schemas (pagination, errors)
│   │   ├── services/            # Business logic layer
│   │   │   ├── __init__.py
│   │   │   ├── auth.py          # Authentication service
│   │   │   ├── course.py        # Course CRUD + logic
│   │   │   ├── note.py          # Note CRUD + search
│   │   │   ├── task.py          # Task CRUD + date filtering
│   │   │   └── sync.py          # Offline sync queue handler
│   │   ├── api/                 # FastAPI route handlers
│   │   │   ├── __init__.py
│   │   │   ├── deps.py          # Dependencies (auth, DB session)
│   │   │   ├── auth.py          # Auth endpoints
│   │   │   ├── courses.py       # Course endpoints
│   │   │   ├── notes.py         # Note endpoints
│   │   │   ├── tasks.py         # Task endpoints
│   │   │   └── search.py        # Search endpoint
│   │   ├── db/                  # Database configuration
│   │   │   ├── __init__.py
│   │   │   ├── session.py       # SQLAlchemy session management
│   │   │   └── init_db.py       # Database initialization
│   │   ├── core/                # Core configuration
│   │   │   ├── __init__.py
│   │   │   ├── config.py        # Settings (Pydantic BaseSettings)
│   │   │   ├── security.py      # Password hashing, JWT
│   │   │   └── exceptions.py    # Custom exception classes
│   │   └── utils/               # Utility functions
│   │       ├── __init__.py
│   │       ├── date_filters.py  # Today/This Week/Upcoming logic
│   │       └── search.py        # Search indexing/querying
│   └── alembic/                 # Database migrations
│       ├── env.py
│       └── versions/
├── tests/
│   ├── contract/                # API contract tests
│   │   ├── test_auth_api.py
│   │   ├── test_courses_api.py
│   │   ├── test_notes_api.py
│   │   ├── test_tasks_api.py
│   │   └── test_search_api.py
│   ├── integration/             # User journey tests
│   │   ├── test_user_journey_p1.py  # US1: Quick capture
│   │   ├── test_user_journey_p2.py  # US2: Unified task view
│   │   ├── test_user_journey_p3.py  # US3: Link tasks to notes
│   │   └── test_offline_sync.py
│   ├── unit/                    # Unit tests for services/utils
│   │   ├── test_date_filters.py
│   │   ├── test_task_service.py
│   │   ├── test_note_service.py
│   │   └── test_search.py
│   ├── conftest.py              # Pytest fixtures
│   └── __init__.py
├── pyproject.toml               # uv/pip project configuration
├── uv.lock                      # uv lockfile
├── .python-version              # Python version specification
├── alembic.ini                  # Alembic migration config
└── README.md

frontend/
├── src/
│   ├── index.html               # Main HTML entry point
│   ├── css/
│   │   ├── main.css             # Tailwind CSS with custom config
│   │   └── components.css       # Component-specific styles
│   ├── js/
│   │   ├── main.js              # App initialization
│   │   ├── api/                 # API client
│   │   │   ├── client.js        # Base HTTP client
│   │   │   ├── auth.js          # Auth API calls
│   │   │   ├── courses.js       # Course API calls
│   │   │   ├── notes.js         # Note API calls
│   │   │   ├── tasks.js         # Task API calls
│   │   │   └── search.js        # Search API calls
│   │   ├── components/          # UI components
│   │   │   ├── course-list.js
│   │   │   ├── note-editor.js
│   │   │   ├── task-list.js
│   │   │   ├── task-views.js    # Today/Week/Upcoming tabs
│   │   │   ├── search-bar.js
│   │   │   └── inbox.js
│   │   ├── utils/
│   │   │   ├── date-helpers.js
│   │   │   ├── storage.js       # LocalStorage for offline queue
│   │   │   └── sync.js          # Offline sync manager
│   │   └── router.js            # Client-side routing
│   └── assets/
│       └── icons/
├── package.json                 # npm for frontend tooling (Tailwind)
├── tailwind.config.js
└── README.md
```

**Structure Decision**: Web application structure with separate backend (FastAPI/Python) and frontend (HTML/CSS/JS with Tailwind). Backend follows domain-driven design with models/schemas/services/api layers for separation of concerns. Frontend uses vanilla JS with component-based structure for simplicity and fast load times (avoiding framework overhead per performance requirements).

## Complexity Tracking

> **Constitution Check PASSED - No violations to justify**

All design decisions align with constitution principles:
- **Simplicity**: SQLite (not PostgreSQL) for MVP, vanilla JS (not React/Vue) for frontend
- **Proven Technology**: FastAPI, SQLAlchemy, pytest are mature and well-documented
- **Single Responsibility**: Clear layer separation (models/schemas/services/API)
- **YAGNI**: No premature optimization, no over-engineering (e.g., no message queues, no microservices)

---

## Phase 0: Research & Decisions

**Status**: ✅ COMPLETE  
**Output**: [research.md](./research.md)

### Resolved Technical Unknowns

All "NEEDS CLARIFICATION" items from Technical Context have been researched and resolved:

1. **Backend Framework**: FastAPI (async support, type safety, auto-docs)
2. **Database**: SQLite for MVP with PostgreSQL migration path
3. **ORM & Validation**: SQLAlchemy 2.0 + Pydantic v2
4. **Testing Tools**: pytest + pytest-asyncio + httpx TestClient
5. **Offline Sync**: Last-Write-Wins with timestamp conflict resolution
6. **Rich Text Editor**: contenteditable + Markdown storage (marked.js for rendering)
7. **Search Implementation**: SQLite FTS5 with Porter stemming
8. **Frontend**: Vanilla JavaScript + Tailwind CSS (no framework)
9. **Package Manager**: uv (per user requirement, 10-100x faster than pip)
10. **API Design**: RESTful JSON API with OpenAPI 3.1

### Key Architecture Decisions

| Decision | Choice | Constitution Principle |
|----------|--------|------------------------|
| Backend | FastAPI | Type safety (I.D), Performance (IV.B) |
| Database | SQLite → PostgreSQL | Simplicity (I.A), Search (IV.B) |
| Frontend | Vanilla JS + Tailwind | Simplicity (I.A), Load time (IV.C) |
| Sync | Last-Write-Wins | Simplicity (I.A), User feedback (III.B) |
| Editor | contenteditable + MD | Simplicity (I.A), Fast typing (IV.A) |

---

## Phase 1: Design & Contracts

**Status**: ✅ COMPLETE  
**Outputs**: 
- [data-model.md](./data-model.md)
- [contracts/api-specification.md](./contracts/api-specification.md)
- [contracts/openapi.yaml](./contracts/openapi.yaml)
- [quickstart.md](./quickstart.md)

### Data Model Summary

**Core Entities**:
1. **User**: Authentication and profile (email, hashed password)
2. **Course**: Organizational container (name, color, archive status)
3. **Note**: Rich text content (Markdown, tags, FTS5 indexed)
4. **Task**: Todo items (due date, priority, completion state)
5. **Subtask**: Child tasks via self-referential foreign key
6. **NoteTaskLink**: Many-to-many association table

**Key Relationships**:
- User 1:N Course
- Course 1:N Note
- Course 1:N Task
- Task 1:N Subtask (self-referential)
- Note M:N Task (via NoteTaskLink)

**Validation Rules**:
- Email: Valid format, unique, indexed
- Course deletion: Cascade to notes and tasks (per Clarification #1)
- Empty task titles: Auto-generate "Untitled Task - {timestamp}" (per Clarification #5)
- Subtask orphaning: Promote to top-level on parent deletion (per Clarification #2)

### API Contract Summary

**Endpoint Groups**:
- **Auth**: `/api/v1/auth/register`, `/api/v1/auth/login`
- **Courses**: CRUD at `/api/v1/courses` and `/api/v1/courses/{id}`
- **Notes**: CRUD at `/api/v1/notes`, list at `/api/v1/courses/{id}/notes`
- **Tasks**: CRUD at `/api/v1/tasks`, list at `/api/v1/courses/{id}/tasks`
- **Search**: `/api/v1/search?q={query}` with FTS5
- **Sync**: `/api/v1/sync` with conflict resolution

**Performance Targets**:
- All endpoints: <200ms P95 latency
- Search: <1s P95 latency
- Auto-generated OpenAPI schema at `/docs`

### Agent Context Update

✅ Updated `.github/agents/copilot-instructions.md` with:
- Python 3.14+ language requirement
- FastAPI, SQLAlchemy, Pydantic framework stack
- SQLite database with offline-first architecture
- pytest testing framework

---

## Phase 2: Implementation Guide

**Status**: ⏳ READY FOR IMPLEMENTATION  
**Output**: Follow this guide + run `/speckit.tasks` for atomic task breakdown

This section provides a **bridge** between design artifacts and implementation, with explicit references to where developers can find the detailed specifications needed at each step.

---

### Implementation Sequence Overview

```
[Project Setup] → [Database Layer] → [Auth & Security] → [Core Features] → [Advanced Features] → [Frontend] → [Polish]
     ↓                  ↓                   ↓                  ↓                    ↓              ↓            ↓
  quickstart.md    data-model.md      research.md §4      spec.md US1-3       spec.md US4-7    research.md  constitution
```

---

### Step 1: Project Initialization (Day 1, ~2 hours)

**Reference Document**: [quickstart.md](./quickstart.md) § 1-3

**Objective**: Bootstrap project with correct Python version, dependencies, and database configuration

**Action Items**:
1. Run `uv init study-helper` per [quickstart.md § 1](./quickstart.md#1-project-initialization)
2. Create directory structure matching [plan.md § Project Structure](#project-structure)
3. Configure `pyproject.toml` with dependencies from [quickstart.md § 2](./quickstart.md#2-install-dependencies)
4. Set up database engine per [quickstart.md § 3](./quickstart.md#3-database-setup)
5. Initialize Alembic migrations

**Success Criteria**:
- `uv run python --version` shows Python 3.14+
- `uv run alembic current` shows no errors
- Directory structure matches backend/ layout in Project Structure above

**Constitution Gates**:
- ✅ Uses `uv` (user requirement)
- ✅ Type safety enabled (`mypy` in dev dependencies)

---

### Step 2: Database Models Implementation (Day 1-2, ~4 hours)

**Reference Documents**:
- Primary: [data-model.md § 2](./data-model.md#2-sqlalchemy-models) (complete model code)
- Supporting: [research.md § 3](./research.md#3-orm-and-data-validation) (SQLAlchemy rationale)
- Validation: [spec.md Clarifications](./spec.md#clarifications) (business rules)

**Objective**: Implement all SQLAlchemy ORM models with proper relationships, indexes, and validation

**Action Items** (in dependency order):
1. **User Model** ([data-model.md § 2.1](./data-model.md#21-user-model))
   - Copy SQLAlchemy model code to `src/study_helper/models/user.py`
   - Note: Email uniqueness constraint for login
   
2. **Course Model** ([data-model.md § 2.2](./data-model.md#22-course-model))
   - Implement with `user_id` foreign key
   - Add cascade delete per [spec.md Clarification #1](./spec.md#clarifications)
   - Color validation (hex format) handled in Pydantic layer
   
3. **Note Model** ([data-model.md § 2.3](./data-model.md#23-note-model))
   - Implement with `course_id` foreign key
   - Add composite index `(course_id, created_at)` for FR-016 (sorting)
   - **Do NOT implement FTS5 yet** (defer to Step 7)
   
4. **Task Model** ([data-model.md § 2.4](./data-model.md#24-task-model))
   - Implement with self-referential `parent_task_id` foreign key
   - Add composite indexes for date filtering (FR-021, FR-029)
   - Implement `TaskPriority` enum (low/medium/high)
   - Add cascade delete for subtasks per [data-model.md § 2.4 State Transitions](./data-model.md#24-task-model)
   
5. **NoteTaskLink Model** ([data-model.md § 2.5](./data-model.md#25-notetasklink-model-association-table))
   - Implement many-to-many relationship table
   - Add composite primary key `(note_id, task_id)`

**Alembic Migration**:
```powershell
uv run alembic revision --autogenerate -m "Add core models: User, Course, Note, Task, NoteTaskLink"
uv run alembic upgrade head
```

**Success Criteria**:
- All models pass `uv run mypy src/study_helper/models` (type safety)
- Migration runs without errors
- Database schema matches [data-model.md § 4 indexes](./data-model.md#4-database-indexes-strategy)

**Constitution Gates**:
- ✅ Single Responsibility: Each model = one entity
- ✅ Type Safety: All fields use `Mapped[T]` type hints
- ✅ Simplicity: No premature optimization (e.g., no caching layer yet)

**Testing** (TDD - Write these BEFORE implementing models):
```python
# tests/unit/test_models.py
def test_user_creation():
    """Verify user model creates with email uniqueness"""
    # Reference: data-model.md § 2.1
    
def test_course_cascade_delete():
    """Verify deleting course deletes notes/tasks (Clarification #1)"""
    # Reference: spec.md Clarifications
    
def test_task_subtask_relationship():
    """Verify self-referential task relationship works"""
    # Reference: data-model.md § 2.4
```

---

### Step 3: Pydantic Schemas (Day 2, ~3 hours)

**Reference Documents**:
- Primary: [contracts/api-specification.md](./contracts/api-specification.md) (request/response shapes)
- Supporting: [research.md § 3](./research.md#3-orm-and-data-validation) (Pydantic rationale)
- Validation Rules: [data-model.md § 5](./data-model.md#5-data-validation-summary)

**Objective**: Create Pydantic schemas for request validation and response serialization

**Action Items** (create in `src/study_helper/schemas/`):

1. **Common Schemas** (`schemas/common.py`)
   - `PaginationParams`: limit, offset
   - `ErrorResponse`: code, message, field (per [api-specification.md Error Format](./contracts/api-specification.md#standard-error-format))
   
2. **User Schemas** (`schemas/user.py`)
   - `UserRegister`: email, password, full_name (per [api-spec § POST /auth/register](./contracts/api-specification.md#post-apiv1authregister))
   - `UserLogin`: email, password
   - `UserResponse`: id, email, full_name, created_at (NO password!)
   - `TokenResponse`: access_token, token_type, user
   
3. **Course Schemas** (`schemas/course.py`)
   - `CourseCreate`: name, description, color (per [api-spec § POST /courses](./contracts/api-specification.md#post-apiv1courses))
   - `CourseUpdate`: name, description, color, is_archived (all optional)
   - `CourseResponse`: all fields + notes_count, tasks_count
   - Validation: `color` must match `#[0-9A-Fa-f]{6}` regex
   
4. **Note Schemas** (`schemas/note.py`)
   - `NoteCreate`: course_id, title, content, tags
   - `NoteUpdate`: title, content, tags (all optional)
   - `NoteResponse`: all fields + linked_tasks list
   - Validation: title max 300 chars, content max 50K chars (per [data-model.md § 2.3](./data-model.md#23-note-model))
   
5. **Task Schemas** (`schemas/task.py`)
   - `TaskCreate`: course_id, title, description, due_date, priority, parent_task_id
   - `TaskUpdate`: all fields optional + is_completed
   - `TaskResponse`: all fields + subtasks array + linked_notes_count
   - Validation: Implement auto-title generation logic per [spec.md Clarification #5](./spec.md#clarifications)

**Pattern Implementation** (from [research.md § 3](./research.md#3-orm-and-data-validation)):
```python
# Example: CourseCreate schema
from pydantic import BaseModel, Field
from typing import Optional

class CourseCreate(BaseModel):
    name: str = Field(..., max_length=200, description="Course name")
    description: Optional[str] = Field(None, max_length=2000)
    color: str = Field(
        default="#3B82F6",
        pattern=r"^#[0-9A-Fa-f]{6}$",
        description="Hex color code"
    )
```

**Success Criteria**:
- All schemas pass `uv run mypy src/study_helper/schemas`
- Pydantic validation raises errors for invalid inputs (test with pytest)

**Testing** (TDD):
```python
# tests/unit/test_schemas.py
def test_course_create_valid_color():
    """Valid hex colors pass validation"""
    # Reference: data-model.md § 2.2 validation rules
    
def test_task_auto_title_generation():
    """Empty title generates 'Untitled Task - {timestamp}'"""
    # Reference: spec.md Clarification #5
```

---

### Step 4: Authentication & Security (Day 3, ~4 hours)

**Reference Documents**:
- Primary: [quickstart.md § 3](./quickstart.md#3-database-setup) (JWT config)
- Supporting: [research.md § 4](./research.md#4-testing-strategy) (security testing)
- API Contract: [api-specification.md § Auth](./contracts/api-specification.md#authentication-endpoints)

**Objective**: Implement JWT-based authentication with password hashing

**Action Items**:

1. **Security Utilities** (`src/study_helper/core/security.py`)
   ```python
   from passlib.context import CryptContext
   from jose import jwt
   from datetime import datetime, timedelta
   
   pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
   
   def hash_password(password: str) -> str:
       """Hash password with bcrypt"""
       return pwd_context.hash(password)
   
   def verify_password(plain: str, hashed: str) -> bool:
       """Verify password against hash"""
       return pwd_context.verify(plain, hashed)
   
   def create_access_token(data: dict, expires_delta: timedelta) -> str:
       """Create JWT token"""
       # Implementation per quickstart.md § 3
   ```

2. **Auth Service** (`src/study_helper/services/auth.py`)
   - `register_user()`: Hash password, create user, return UserResponse
   - `authenticate_user()`: Verify email/password, return user or None
   - `create_token()`: Generate JWT with user_id claim
   
3. **Auth Dependencies** (`src/study_helper/api/deps.py`)
   ```python
   from fastapi import Depends, HTTPException, status
   from fastapi.security import HTTPBearer
   
   security = HTTPBearer()
   
   async def get_current_user(token: str = Depends(security)) -> User:
       """Extract and validate JWT, return current user"""
       # Implementation per api-specification.md Auth section
   ```

4. **Auth Endpoints** (`src/study_helper/api/auth.py`)
   - `POST /api/v1/auth/register` (per [api-spec](./contracts/api-specification.md#post-apiv1authregister))
   - `POST /api/v1/auth/login` (per [api-spec](./contracts/api-specification.md#post-apiv1authlogin))

**Success Criteria**:
- Register creates user with hashed password (never store plain text)
- Login returns valid JWT token
- Protected endpoints reject invalid/missing tokens

**Testing** (TDD - **100% coverage required** per constitution):
```python
# tests/contract/test_auth_api.py
def test_register_success():
    """POST /auth/register with valid data returns 201"""
    # Reference: api-specification.md § POST /auth/register
    
def test_login_invalid_credentials():
    """POST /auth/login with wrong password returns 401"""
    # Reference: api-specification.md errors
    
def test_protected_endpoint_requires_token():
    """GET /courses without token returns 401"""
    # Reference: constitution § II.C (100% critical path coverage)
```

---

### Step 5: Core CRUD Services (Day 3-5, ~8 hours)

**Reference Documents**:
- API Contracts: [api-specification.md](./contracts/api-specification.md) (all endpoints)
- Business Rules: [spec.md User Stories 1-3](./spec.md#user-story-1---quick-capture-and-basic-organization-priority-p1)
- Data Model: [data-model.md § 5](./data-model.md#5-data-validation-summary) (business rules)

**Objective**: Implement service layer for courses, notes, tasks with business logic

**Action Items**:

1. **Course Service** (`src/study_helper/services/course.py`)
   - `create_course(user_id, data: CourseCreate)` → Course
   - `get_courses(user_id, is_archived: bool)` → List[Course]
   - `update_course(course_id, user_id, data: CourseUpdate)` → Course
   - `delete_course(course_id, user_id)` → None
     - **Critical**: Verify cascade delete works (Clarification #1)
     - Test: Deleting course deletes all notes and tasks
   
2. **Note Service** (`src/study_helper/services/note.py`)
   - `create_note(data: NoteCreate)` → Note
   - `get_notes_by_course(course_id, sort_by, order)` → List[Note]
     - Implement sorting per [spec.md FR-016](./spec.md) (newest first by default)
   - `update_note(note_id, data: NoteUpdate)` → Note
   - `delete_note(note_id)` → None
     - **Critical**: Remove note-task links but keep tasks (per data-model)
   - `link_note_to_task(note_id, task_id)` → NoteTaskLink
   - `unlink_note_from_task(note_id, task_id)` → None
   
3. **Task Service** (`src/study_helper/services/task.py`)
   - `create_task(data: TaskCreate)` → Task
     - Implement auto-title generation if title empty (Clarification #5)
   - `get_tasks_by_course(course_id, view, completed, sort_by)` → List[Task]
     - Implement "Today", "This Week", "Upcoming" filters (User Story 2)
     - Reference: [spec.md US2 Acceptance Scenarios](./spec.md#user-story-2---unified-task-view-and-time-management-priority-p2)
   - `update_task(task_id, data: TaskUpdate)` → Task
     - Set `completed_at` when `is_completed` changes to True
   - `delete_task(task_id)` → None
     - **Critical**: Promote subtasks to top-level (Clarification #2)
     - Test: Set `parent_task_id = NULL` on all subtasks

**Date Filtering Logic** (`src/study_helper/utils/date_filters.py`):
```python
from datetime import datetime, timedelta

def is_today(due_date: datetime) -> bool:
    """Check if due_date is today"""
    return due_date.date() == datetime.utcnow().date()

def is_this_week(due_date: datetime) -> bool:
    """Check if due_date is within next 7 days (including today)"""
    # Reference: spec.md Clarification #4
    today = datetime.utcnow().date()
    week_end = today + timedelta(days=7)
    return today <= due_date.date() <= week_end

def is_upcoming(due_date: datetime) -> bool:
    """Check if due_date is beyond this week"""
    week_end = datetime.utcnow().date() + timedelta(days=7)
    return due_date.date() > week_end
```

**Success Criteria**:
- All services return correct data per API contracts
- Business rules from spec.md are enforced
- Services are testable in isolation (use in-memory SQLite)

**Testing** (TDD - **90% coverage required** per constitution):
```python
# tests/integration/test_user_journey_p1.py
def test_us1_quick_capture_workflow():
    """Verify User Story 1 end-to-end flow"""
    # 1. Create course "Biology 101"
    # 2. Create note "Cell Structure" in Biology 101
    # 3. Edit note to add content
    # 4. Create task "Study for quiz" with due date
    # 5. Mark task complete
    # Reference: spec.md US1 Acceptance Scenarios
    
# tests/integration/test_user_journey_p2.py
def test_us2_unified_task_view():
    """Verify time-based task filtering works"""
    # Create tasks with dates: today, 3 days out, 10 days out
    # Verify "Today" view shows only today's tasks
    # Verify "This Week" includes today + 7 days
    # Reference: spec.md US2 + Clarification #4
```

---

### Step 6: FastAPI Route Handlers (Day 5-6, ~6 hours)

**Reference Documents**:
- Primary: [contracts/api-specification.md](./contracts/api-specification.md) (complete API reference)
- OpenAPI: [contracts/openapi.yaml](./contracts/openapi.yaml) (machine-readable spec)

**Objective**: Expose services via RESTful API endpoints with proper error handling

**Action Items** (create in `src/study_helper/api/`):

1. **Course Routes** (`api/courses.py`)
   - Implement all endpoints from [api-spec § Course Endpoints](./contracts/api-specification.md#course-endpoints)
   - Use `get_current_user` dependency for authentication
   - Return proper HTTP status codes (200, 201, 204, 400, 401, 404)
   
2. **Note Routes** (`api/notes.py`)
   - Implement all endpoints from [api-spec § Note Endpoints](./contracts/api-specification.md#note-endpoints)
   - Include `POST /notes/{note_id}/link-task` for linking
   
3. **Task Routes** (`api/tasks.py`)
   - Implement all endpoints from [api-spec § Task Endpoints](./contracts/api-specification.md#task-endpoints)
   - Handle query parameters: `view`, `completed`, `sort_by`, `order`
   
4. **Main App** (`main.py`)
   - Update to include routers:
   ```python
   from src.study_helper.api import auth, courses, notes, tasks
   
   app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
   app.include_router(courses.router, prefix="/api/v1/courses", tags=["courses"])
   app.include_router(notes.router, prefix="/api/v1/notes", tags=["notes"])
   app.include_router(tasks.router, prefix="/api/v1/tasks", tags=["tasks"])
   ```

**Error Handling** (`core/exceptions.py`):
```python
from fastapi import HTTPException, status

class NotFoundError(HTTPException):
    def __init__(self, resource: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "NOT_FOUND", "message": f"{resource} not found"}}
        )

class ForbiddenError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": {"code": "FORBIDDEN", "message": "User does not own this resource"}}
        )
```

**Success Criteria**:
- All endpoints return responses matching [api-specification.md](./contracts/api-specification.md)
- OpenAPI docs at `/docs` match [openapi.yaml](./contracts/openapi.yaml)
- Performance: <200ms P95 latency (test with `pytest-benchmark`)

**Testing** (TDD - **100% coverage** for critical paths):
```python
# tests/contract/test_courses_api.py
def test_create_course_success():
    """POST /courses with valid data returns 201"""
    response = client.post("/api/v1/courses", json={
        "name": "Biology 101",
        "description": "Cell biology",
        "color": "#10B981"
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 201
    assert response.json()["name"] == "Biology 101"
    # Reference: api-specification.md § POST /courses

def test_get_courses_unauthorized():
    """GET /courses without token returns 401"""
    response = client.get("/api/v1/courses")
    assert response.status_code == 401
```

---

### Step 7: Search Implementation (Day 7, ~4 hours)

**Reference Documents**:
- Primary: [research.md § 7](./research.md#7-search-implementation) (FTS5 setup)
- Data Model: [data-model.md § 3](./data-model.md#3-full-text-search-fts5) (FTS triggers)
- API Contract: [api-specification.md § Search](./contracts/api-specification.md#search-endpoint)
- User Story: [spec.md US5](./spec.md#user-story-5---search-and-discovery-priority-p5)

**Objective**: Implement full-text search with <1s latency for 1000 notes

**Action Items**:

1. **FTS5 Setup** (`src/study_helper/db/fts_setup.py`)
   - Create virtual table: `notes_fts` (per [data-model.md § 3](./data-model.md#3-full-text-search-fts5))
   - Add triggers for INSERT/UPDATE/DELETE on notes table
   - Use Porter stemming tokenizer for better matches
   
2. **Alembic Migration**:
   ```powershell
   uv run alembic revision -m "Add FTS5 search for notes"
   # Manually add FTS5 SQL from data-model.md § 3
   uv run alembic upgrade head
   ```

3. **Search Service** (`src/study_helper/services/search.py`)
   ```python
   async def search_notes(user_id: int, query: str, limit: int = 50):
       """Full-text search across user's notes"""
       # Use FTS5 MATCH query from data-model.md § 3
       # Filter by user_id (join through course → user)
       # Return results with BM25 ranking
       # Include snippet highlighting
   ```

4. **Search Endpoint** (`api/search.py`)
   - `GET /api/v1/search?q={query}&limit={limit}`
   - Return format per [api-specification.md](./contracts/api-specification.md#get-apiv1search)

**Success Criteria**:
- Search finds notes by title and content
- Porter stemming works: "running" finds "run"
- Performance: <1s for 1000 notes (constitution requirement)

**Testing**:
```python
# tests/contract/test_search_performance.py
@pytest.mark.benchmark
def test_search_performance_1000_notes():
    """Search across 1000 notes completes in <1s"""
    # Create 1000 notes with varied content
    # Search for common term
    # Assert response time < 1000ms
    # Reference: constitution § IV.B, spec.md US5
```

---

### Step 8: Offline Sync (Day 8, ~5 hours)

**Reference Documents**:
- Primary: [research.md § 5](./research.md#5-offline-first-sync-architecture) (LWW strategy)
- API Contract: [api-specification.md § Sync](./contracts/api-specification.md#post-apiv1sync)
- Clarification: [spec.md Clarification #3](./spec.md#clarifications) (conflict resolution)

**Objective**: Implement Last-Write-Wins sync with client change queue

**Action Items**:

1. **Sync Service** (`src/study_helper/services/sync.py`)
   ```python
   async def sync_changes(user_id: int, changes: List[ChangeRecord], last_sync_at: datetime):
       """Process client changes and return server changes + conflicts"""
       conflicts = []
       applied = 0
       
       for change in changes:
           server_record = await get_record(change.type, change.id)
           if server_record.updated_at > change.updated_at:
               # Server wins (Last-Write-Wins)
               conflicts.append({
                   "type": change.type,
                   "id": change.id,
                   "resolution": "server_wins",
                   "message": "Record updated on server more recently"
               })
           else:
               # Apply client change
               await apply_change(change)
               applied += 1
       
       # Get server changes since last_sync_at
       server_changes = await get_changes_since(user_id, last_sync_at)
       
       return {
           "applied": applied,
           "conflicts": conflicts,
           "server_changes": server_changes,
           "new_sync_timestamp": datetime.utcnow()
       }
   ```

2. **Sync Endpoint** (`api/sync.py`)
   - `POST /api/v1/sync` per [api-specification.md](./contracts/api-specification.md#post-apiv1sync)

**Success Criteria**:
- Conflicts resolved with Last-Write-Wins (server timestamp authoritative)
- Client receives server changes since last sync
- User notified of conflicts (via response, frontend shows toast)

**Testing**:
```python
# tests/integration/test_offline_sync.py
def test_conflict_resolution_server_wins():
    """When server has newer timestamp, server change wins"""
    # Client: Update note at T1
    # Server: Update same note at T2 (T2 > T1)
    # Client syncs → server change wins
    # Reference: spec.md Clarification #3, research.md § 5
```

---

### Step 9: Frontend Implementation (Day 9-12, ~16 hours)

**Reference Documents**:
- Architecture: [research.md § 8](./research.md#8-frontend-architecture) (vanilla JS + Tailwind)
- UX Requirements: [spec.md all User Stories](./spec.md#user-scenarios--testing-mandatory)
- Performance: Constitution Principle IV (< 2s page load, < 100ms interactions)

**Objective**: Build responsive web UI with offline-first architecture

**Action Items**:

1. **HTML Structure** (`templates/index.html`)
   - Semantic HTML5 with ARIA labels (WCAG 2.1 AA compliance)
   - Tailwind CSS CDN (defer to custom build later)
   - Main sections: Header, CourseList, NoteEditor, TaskViews, SearchBar
   
2. **API Client** (`src/js/api/`)
   - Base HTTP client with JWT token injection
   - Methods for all endpoints from [api-specification.md](./contracts/api-specification.md)
   - Offline queue: Store failed requests in LocalStorage
   
3. **Components** (`src/js/components/`)
   - `course-list.js`: Render courses, handle create/archive (US1)
   - `note-editor.js`: Rich text editing with Markdown conversion (US1)
   - `task-list.js`: Task CRUD with subtasks (US4)
   - `task-views.js`: Today/This Week/Upcoming tabs (US2)
   - `search-bar.js`: Full-text search with results (US5)
   
4. **Offline Sync** (`src/js/utils/sync.js`)
   - Detect online/offline events
   - Queue changes in LocalStorage when offline
   - Sync on reconnect per [research.md § 5](./research.md#5-offline-first-sync-architecture)
   - Show toast notifications for conflicts

**Success Criteria**:
- <2s initial page load (constitution requirement)
- <100ms UI interactions (typing, clicking)
- Keyboard navigation works (Tab, Enter, Esc)
- 4.5:1 color contrast (WCAG 2.1 AA)

**Testing** (Manual + E2E):
```javascript
// tests/e2e/test_user_stories.js (using Playwright or similar)
test('US1: Quick capture workflow', async () => {
  // Create course → create note → edit note → create task → mark complete
  // Reference: spec.md US1 Acceptance Scenarios
});
```

---

### Step 10: Performance Optimization (Day 13, ~4 hours)

**Reference Documents**:
- Indexes: [data-model.md § 4](./data-model.md#4-database-indexes-strategy)
- Performance: Constitution Principle IV (all latency targets)

**Objective**: Ensure all performance requirements are met

**Action Items**:

1. **Database Query Optimization**
   - Verify all indexes from [data-model.md § 4](./data-model.md#4-database-indexes-strategy) exist
   - Use SQLAlchemy `selectinload()` to prevent N+1 queries
   - Add pagination to list endpoints (limit 50 default)
   
2. **API Middleware** (`main.py`)
   ```python
   from time import time
   
   @app.middleware("http")
   async def log_request_time(request, call_next):
       start = time()
       response = await call_next(request)
       duration = time() - start
       response.headers["X-Response-Time"] = f"{duration:.3f}s"
       if duration > 0.2:  # >200ms warning
           logger.warning(f"Slow request: {request.url} took {duration:.3f}s")
       return response
   ```

3. **Frontend Optimization**
   - Lazy load notes/tasks (pagination)
   - Debounce search input (300ms delay)
   - Cache course list in LocalStorage
   
4. **Performance Testing**
   ```python
   # tests/contract/test_performance.py
   @pytest.mark.benchmark
   def test_api_latency_p95():
       """P95 latency for all endpoints < 200ms"""
       # Run 100 requests per endpoint
       # Assert 95th percentile < 200ms
   ```

**Success Criteria**:
- All endpoints meet <200ms P95 latency
- Search meets <1s latency
- Page load <2s
- UI interactions <100ms

---

### Constitution Compliance Checklist

Before merging to master, verify ALL gates pass:

**Code Quality** (Principle I):
- [ ] All functions have single responsibility
- [ ] Type hints on all functions (mypy passes)
- [ ] No code duplication (DRY principle)
- [ ] Error handling with structured responses

**Test-First** (Principle II):
- [ ] 100% coverage: auth, date filtering, note-task linking
- [ ] 90% coverage: CRUD services
- [ ] 80% overall coverage
- [ ] All tests pass (`uv run pytest`)

**UX Consistency** (Principle III):
- [ ] Tailwind design system used throughout
- [ ] WCAG 2.1 AA compliance (contrast, keyboard nav)
- [ ] User-friendly error messages
- [ ] Loading states for >500ms operations

**Performance** (Principle IV):
- [ ] <500ms note/task creation
- [ ] <100ms UI interactions
- [ ] <200ms P95 API latency
- [ ] <1s search latency
- [ ] <2s page load

---

### Quick Reference Map

When implementing, find specifications here:

| What You're Building | Primary Reference | Supporting Docs |
|---------------------|-------------------|-----------------|
| SQLAlchemy models | [data-model.md § 2](./data-model.md#2-sqlalchemy-models) | [research.md § 3](./research.md#3-orm-and-data-validation) |
| Pydantic schemas | [api-specification.md](./contracts/api-specification.md) | [data-model.md § 5](./data-model.md#5-data-validation-summary) |
| Service business logic | [spec.md User Stories](./spec.md#user-scenarios--testing-mandatory) | [data-model.md § 5](./data-model.md#5-data-validation-summary) |
| API endpoints | [api-specification.md](./contracts/api-specification.md) | [openapi.yaml](./contracts/openapi.yaml) |
| Auth/JWT | [quickstart.md § 3](./quickstart.md#3-database-setup) | [research.md § 4](./research.md#4-testing-strategy) |
| Search (FTS5) | [data-model.md § 3](./data-model.md#3-full-text-search-fts5) | [research.md § 7](./research.md#7-search-implementation) |
| Offline sync | [research.md § 5](./research.md#5-offline-first-sync-architecture) | [api-spec § Sync](./contracts/api-specification.md#post-apiv1sync) |
| Date filtering | [spec.md US2](./spec.md#user-story-2---unified-task-view-and-time-management-priority-p2) | [spec.md Clarification #4](./spec.md#clarifications) |
| Frontend components | [research.md § 8](./research.md#8-frontend-architecture) | [spec.md all User Stories](./spec.md) |
| Project setup | [quickstart.md](./quickstart.md) | [plan.md § Project Structure](#project-structure) |

---

### Atomic Task Breakdown (Optional)

For detailed task-by-task breakdown with estimated hours, run:

```bash
/speckit.tasks
```

This generates `tasks.md` with:
- Every task sequenced for TDD workflow
- Test specifications written before code
- Estimated time per task
- Dependencies between tasks

---

## Gate Check: Constitution Compliance Post-Design

**Re-evaluating Constitution Check after Phase 1 design:**

✅ **Code Quality**: 
- Single responsibility maintained (models/schemas/services/API separation)
- Type safety via Pydantic + SQLAlchemy typed models
- Error handling documented in API specification

✅ **Test-First**:
- Contract tests: OpenAPI schema validation
- Integration tests: User journeys with TestClient
- Unit tests: Models and service logic in isolation

✅ **UX Consistency**:
- Tailwind CSS enforces design system
- WCAG 2.1 AA requirements in frontend design
- Toast notifications for user feedback

✅ **Performance**:
- SQLite FTS5 for <1s search
- Composite indexes for date filtering
- Async FastAPI for <200ms API latency

**Violations**: NONE  
**Justifications Required**: NONE

---

## Next Command

Run the following to generate detailed implementation tasks:

```bash
# Generate tasks.md with RED-GREEN-REFACTOR workflow
/speckit.tasks
```

**What it will do**:
1. Break down each user story into atomic tasks
2. Generate test specifications before implementation code
3. Sequence tasks for incremental delivery
4. Enforce TDD workflow (write test → fail → implement → pass → refactor)

---

## Planning Phase Complete

**Branch**: `001-student-knowledge-app`  
**Artifacts Generated**:
- ✅ `plan.md` (this file)
- ✅ `research.md` (technology decisions)
- ✅ `data-model.md` (entities and relationships)
- ✅ `contracts/api-specification.md` (endpoint documentation)
- ✅ `contracts/openapi.yaml` (machine-readable schema)
- ✅ `quickstart.md` (setup instructions)

**Agent Context Updated**:
- ✅ `.github/agents/copilot-instructions.md`

**Ready for**:
- `/speckit.tasks` to generate implementation tasks
- Project initialization via `quickstart.md`
- Test-driven development workflow
