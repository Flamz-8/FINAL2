# Tasks: Student Knowledge Management App

**Input**: Design documents from `/specs/001-student-knowledge-app/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Constitution Compliance**: This template enforces Test-First Development (Constitution Principle II). Tests MUST be written and approved before implementation. Each user story phase follows Red-Green-Refactor workflow.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

---

## Format: `- [ ] [ID] [P?] [Story?] Description`

- **Checkbox**: `- [ ]` for incomplete, `- [x]` for complete
- **[ID]**: Sequential task number (T001, T002, T003...)
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story (US1, US2, US3...) - omit for Setup/Foundational
- **File path**: Include exact file path in description

---

## Implementation Strategy

**MVP Scope**: User Story 1 (P1) provides immediate value - students can capture notes and tasks.

**Incremental Delivery**:
1. **Phase 1 (Setup)**: Project initialization - blocks all other work
2. **Phase 2 (Foundational)**: Auth & database - blocks user stories
3. **Phase 3 (US1 - P1)**: Quick capture & organization - **MVP COMPLETE**
4. **Phase 4 (US2 - P2)**: Time-based task views
5. **Phase 5 (US3 - P3)**: Note-task linking
6. **Phase 6 (US4 - P4)**: Subtasks
7. **Phase 7 (US5 - P5)**: Search
8. **Phase 8 (US6 - P6)**: Inbox (optional)
9. **Phase 9 (US7 - P7)**: Notifications (optional)
10. **Phase 10 (Polish)**: Performance, UX, accessibility

---

## Dependency Graph

```
Setup (Phase 1)
  ↓
Foundational (Phase 2: Auth + DB)
  ↓
US1 [P1] → US2 [P2] → US3 [P3]
                          ↓
                       US4 [P4]
  ↓
US5 [P5] (independent)
  ↓
US6 [P6] (optional)
  ↓
US7 [P7] (optional)
  ↓
Polish (Phase 10)
```

**Parallel Opportunities**:
- Within Phase 2: Models, schemas, and tests can be parallelized per entity
- US5 (Search) can be implemented in parallel with US2-US4 (uses same Note model)
- Frontend components per user story are independent

---

## Phase 1: Setup (Project Initialization)

**Purpose**: Bootstrap project structure and tooling  
**Blocks**: All other phases  
**Reference**: [quickstart.md](./quickstart.md)

### Project Structure

- [x] T001 Initialize Python project with uv in `backend/` directory
- [x] T002 Create directory structure per plan.md (backend/src/study_helper/, backend/tests/)
- [x] T003 Create directory structure for frontend (frontend/src/, frontend/src/js/, frontend/src/css/)
- [x] T004 Configure pyproject.toml with FastAPI, SQLAlchemy, Pydantic, pytest dependencies
- [x] T005 [P] Create .env file with DATABASE_URL and SECRET_KEY configuration
- [x] T006 [P] Create .gitignore for Python, Node, SQLite, env files

### Database Configuration

- [x] T007 Create backend/src/study_helper/core/config.py with Pydantic Settings
- [x] T008 Create backend/src/study_helper/db/base.py with SQLAlchemy async engine setup
- [x] T009 Initialize Alembic with `alembic init migrations` in backend/
- [x] T010 Configure alembic.ini with SQLite database URL
- [x] T011 Update migrations/env.py to import Base metadata from db/base.py

### Verification

- [x] T012 Verify `uv run python --version` shows Python 3.14+
- [x] T013 Verify `uv run alembic current` runs without errors
- [x] T014 Create backend/README.md with quickstart instructions

**Success Criteria**: Project structure exists, dependencies installed, Alembic initialized

---

## Phase 2: Foundational (Auth & Database)

**Purpose**: Authentication system and core database models  
**Blocks**: All user stories  
**Reference**: [data-model.md](./data-model.md), [api-specification.md](./contracts/api-specification.md)

### User Model & Auth (Blocks All User Stories)

**Test Setup**:
- [x] T015 Create backend/tests/conftest.py with pytest fixtures (async client, test database)
- [x] T016 Create backend/tests/unit/test_models.py file structure

**TDD: User Model**:
- [x] T017 **[RED]** Write test_user_creation() verifying User model with email uniqueness
- [x] T018 **[RED]** Write test_user_email_index() verifying email index exists for login performance
- [x] T019 **[GREEN]** Create backend/src/study_helper/models/user.py with User model per data-model.md § 2.1
- [x] T020 **[GREEN]** Run migration: `alembic revision --autogenerate -m "Add User model"`
- [x] T021 **[GREEN]** Apply migration: `alembic upgrade head`
- [x] T022 **[GREEN]** Verify tests pass with `uv run pytest tests/unit/test_models.py::test_user_creation`
- [x] T023 **[REFACTOR]** Add type hints validation with mypy, ensure all Mapped[T] types correct

**TDD: Auth Security**:
- [x] T024 **[RED]** Create backend/tests/unit/test_security.py with test_hash_password() and test_verify_password()
- [x] T025 **[GREEN]** Create backend/src/study_helper/core/security.py with bcrypt password hashing
- [x] T026 **[GREEN]** Implement create_access_token() with JWT encoding (24hr expiration)
- [x] T027 **[REFACTOR]** Extract SECRET_KEY to config.py, use settings.SECRET_KEY

**TDD: User Schemas**:
- [x] T028 **[RED]** Create backend/tests/unit/test_schemas.py with test_user_register_validation()
- [x] T029 **[GREEN]** Create backend/src/study_helper/schemas/user.py with UserRegister schema (email, password, full_name)
- [x] T030 **[GREEN]** Create UserResponse schema (id, email, full_name, created_at - NO password)
- [x] T031 **[GREEN]** Create UserLogin schema (email, password)
- [x] T032 **[GREEN]** Create TokenResponse schema (access_token, token_type, user)
- [x] T033 **[REFACTOR]** Add Pydantic validators for email format and password min length (8 chars)

**TDD: Auth Service**:
- [x] T034 **[RED]** Create backend/tests/integration/test_auth_service.py with test_register_user_success()
- [x] T035 **[RED]** Write test_register_duplicate_email_fails() expecting IntegrityError
- [x] T036 **[RED]** Write test_authenticate_user_valid_credentials()
- [x] T037 **[RED]** Write test_authenticate_user_invalid_password_returns_none()
- [x] T038 **[GREEN]** Create backend/src/study_helper/services/auth.py with register_user() function
- [x] T039 **[GREEN]** Implement authenticate_user() function (verify email + password, return User or None)
- [x] T040 **[REFACTOR]** Extract database session management to async context manager

**TDD: Auth API**:
- [x] T041 **[RED]** Create backend/tests/contract/test_auth_api.py with test_register_success()
- [x] T042 **[RED]** Write test_register_duplicate_email_returns_409()
- [x] T043 **[RED]** Write test_login_success_returns_token()
- [x] T044 **[RED]** Write test_login_invalid_credentials_returns_401()
- [x] T045 **[GREEN]** Create backend/src/study_helper/api/deps.py with get_db() dependency
- [x] T046 **[GREEN]** Implement get_current_user() dependency (decode JWT, return User)
- [x] T047 **[GREEN]** Create backend/src/study_helper/api/auth.py with POST /api/v1/auth/register endpoint
- [x] T048 **[GREEN]** Implement POST /api/v1/auth/login endpoint (return TokenResponse)
- [x] T049 **[GREEN]** Update backend/src/study_helper/main.py to include auth router
- [x] T050 **[REFACTOR]** Add error handling for 400 (invalid input), 401 (unauthorized), 409 (conflict)

**Success Criteria**: 
- ✅ 100% test coverage for auth endpoints (constitution requirement)
- ✅ Users can register and login
- ✅ JWT tokens work for protected endpoints

---

## Phase 3: User Story 1 [P1] - Quick Capture & Organization (MVP)

**Goal**: Students can create courses, add notes, create tasks, and view them organized by course  
**Independent Test**: Create course → add note → edit note → create task → mark complete  
**Reference**: [spec.md US1](./spec.md#user-story-1---quick-capture-and-basic-organization-priority-p1)

### Course Entity (US1)

**TDD: Course Model**:
- [x] T051 [US1] **[RED]** Write test_course_creation() in backend/tests/unit/test_models.py
- [x] T052 [US1] **[RED]** Write test_course_cascade_delete() verifying notes and tasks are deleted (Clarification #1)
- [x] T053 [US1] **[GREEN]** Create backend/src/study_helper/models/course.py per data-model.md § 2.2
- [x] T054 [US1] **[GREEN]** Add composite index (user_id, is_archived) for filtering active courses
- [x] T055 [US1] **[GREEN]** Run migration: `alembic revision --autogenerate -m "Add Course model"`
- [x] T056 [US1] **[REFACTOR]** Verify cascade="all, delete-orphan" on notes and tasks relationships

**TDD: Course Schemas**:
- [x] T057 [P] [US1] **[RED]** Write test_course_create_valid_color() in backend/tests/unit/test_schemas.py
- [x] T058 [P] [US1] **[RED]** Write test_course_create_invalid_color_fails() expecting ValidationError
- [x] T059 [P] [US1] **[GREEN]** Create backend/src/study_helper/schemas/course.py with CourseCreate schema
- [x] T060 [P] [US1] **[GREEN]** Add color field with regex pattern ^#[0-9A-Fa-f]{6}$ and default "#3B82F6"
- [x] T061 [P] [US1] **[GREEN]** Create CourseUpdate schema (all fields optional including is_archived)
- [x] T062 [P] [US1] **[GREEN]** Create CourseResponse schema with notes_count and tasks_count fields
- [x] T063 [P] [US1] **[REFACTOR]** Add Field validators for name max 200 chars, description max 2000 chars

**TDD: Course Service**:
- [x] T064 [US1] **[RED]** Create backend/tests/integration/test_course_service.py with test_create_course()
- [x] T065 [US1] **[RED]** Write test_get_courses_filtered_by_archived_status()
- [x] T066 [US1] **[RED]** Write test_update_course_archives_successfully()
- [x] T067 [US1] **[RED]** Write test_delete_course_cascades_to_notes_and_tasks() (critical business rule)
- [x] T068 [US1] **[GREEN]** Create backend/src/study_helper/services/course.py with create_course() function
- [x] T069 [US1] **[GREEN]** Implement get_courses(user_id, is_archived) with filtering
- [x] T070 [US1] **[GREEN]** Implement update_course() with ownership verification (user_id check)
- [x] T071 [US1] **[GREEN]** Implement delete_course() with cascade delete confirmation
- [x] T072 [US1] **[REFACTOR]** Add error handling for ForbiddenError (user doesn't own course)

**TDD: Course API**:
- [x] T073 [US1] **[RED]** Create backend/tests/contract/test_courses_api.py with test_create_course_success()
- [x] T074 [US1] **[RED]** Write test_get_courses_requires_authentication()
- [x] T075 [US1] **[RED]** Write test_update_course_forbidden_if_not_owner()
- [x] T076 [US1] **[RED]** Write test_delete_course_returns_204()
- [x] T077 [US1] **[GREEN]** Create backend/src/study_helper/api/courses.py with POST /api/v1/courses endpoint
- [x] T078 [US1] **[GREEN]** Implement GET /api/v1/courses with is_archived query parameter
- [x] T079 [US1] **[GREEN]** Implement PATCH /api/v1/courses/{course_id} endpoint
- [x] T080 [US1] **[GREEN]** Implement DELETE /api/v1/courses/{course_id} endpoint
- [x] T081 [US1] **[GREEN]** Add courses router to main.py with /api/v1 prefix
- [x] T082 [US1] **[REFACTOR]** Add response models to all endpoints (CourseResponse, List[CourseResponse])

### Note Entity (US1)

**TDD: Note Model**:
- [x] T083 [P] [US1] **[RED]** Write test_note_creation() in backend/tests/unit/test_models.py
- [x] T084 [P] [US1] **[RED]** Write test_note_composite_index_course_created() for sorting performance
- [x] T085 [P] [US1] **[GREEN]** Create backend/src/study_helper/models/note.py per data-model.md § 2.3
- [x] T086 [P] [US1] **[GREEN]** Add composite index (course_id, created_at) for FR-016 sorting requirement
- [x] T087 [P] [US1] **[GREEN]** Add relationship to NoteTaskLink (defer to US3 for M:N implementation)
- [x] T088 [P] [US1] **[GREEN]** Run migration: `alembic revision --autogenerate -m "Add Note model"`

**TDD: Note Schemas**:
- [x] T089 [P] [US1] **[RED]** Write test_note_create_validation() verifying title and content required
- [x] T090 [P] [US1] **[RED]** Write test_note_title_max_length_300() expecting ValidationError if exceeded
- [x] T091 [P] [US1] **[RED]** Write test_note_content_max_length_50000() for large note limit
- [x] T092 [P] [US1] **[GREEN]** Create backend/src/study_helper/schemas/note.py with NoteCreate schema
- [x] T093 [P] [US1] **[GREEN]** Add validation: title max 300 chars, content max 50,000 chars
- [x] T094 [P] [US1] **[GREEN]** Create NoteUpdate schema (title, content, tags all optional)
- [x] T095 [P] [US1] **[GREEN]** Create NoteResponse schema with linked_tasks list (empty for now, populate in US3)

**TDD: Note Service**:
- [x] T096 [US1] **[RED]** Create backend/tests/integration/test_note_service.py with test_create_note()
- [x] T097 [US1] **[RED]** Write test_get_notes_by_course_sorted_newest_first() (FR-016 default sort)
- [x] T098 [US1] **[RED]** Write test_update_note_updates_updated_at_timestamp()
- [x] T099 [US1] **[RED]** Write test_delete_note_succeeds()
- [x] T100 [US1] **[GREEN]** Create backend/src/study_helper/services/note.py with create_note() function
- [x] T101 [US1] **[GREEN]** Implement get_notes_by_course(course_id, sort_by, order) with default order=desc
- [x] T102 [US1] **[GREEN]** Implement update_note() with timestamp update
- [x] T103 [US1] **[GREEN]** Implement delete_note() (removes note-task links but keeps tasks)
- [x] T104 [US1] **[REFACTOR]** Add pagination support (limit 50 default) for note lists

**TDD: Note API**:
- [x] T105 [US1] **[RED]** Create backend/tests/contract/test_notes_api.py with test_create_note_success()
- [x] T106 [US1] **[RED]** Write test_get_notes_by_course_filters_correctly()
- [x] T107 [US1] **[RED]** Write test_update_note_returns_updated_data()
- [x] T108 [US1] **[RED]** Write test_delete_note_returns_204()
- [x] T109 [US1] **[GREEN]** Create backend/src/study_helper/api/notes.py with POST /api/v1/notes endpoint
- [x] T110 [US1] **[GREEN]** Implement GET /api/v1/courses/{course_id}/notes with sort_by and order params
- [x] T111 [US1] **[GREEN]** Implement PATCH /api/v1/notes/{note_id} endpoint
- [x] T112 [US1] **[GREEN]** Implement DELETE /api/v1/notes/{note_id} endpoint
- [x] T113 [US1] **[GREEN]** Add notes router to main.py
- [ ] T114 [US1] **[REFACTOR]** Verify <200ms P95 latency with pytest-benchmark

### Task Entity (US1)

**TDD: Task Model**:
- [x] T115 [P] [US1] **[RED]** Write test_task_creation() in backend/tests/unit/test_models.py
- [x] T116 [P] [US1] **[RED]** Write test_task_auto_title_generation() for empty title (Clarification #5)
- [x] T117 [P] [US1] **[RED]** Write test_task_completed_at_set_when_is_completed_true()
- [x] T118 [P] [US1] **[GREEN]** Create backend/src/study_helper/models/task.py per data-model.md § 2.4
- [x] T119 [P] [US1] **[GREEN]** Add TaskPriority enum (low, medium, high)
- [x] T120 [P] [US1] **[GREEN]** Add self-referential parent_task_id foreign key (for US4 subtasks)
- [x] T121 [P] [US1] **[GREEN]** Add composite indexes (course_id, due_date) and (course_id, created_at)
- [x] T122 [P] [US1] **[GREEN]** Run migration: `alembic revision --autogenerate -m "Add Task model"`

**TDD: Task Schemas**:
- [x] T123 [P] [US1] **[RED]** Write test_task_create_with_empty_title_generates_placeholder()
- [x] T124 [P] [US1] **[RED]** Write test_task_priority_validation() ensuring only low/medium/high allowed
- [x] T125 [P] [US1] **[GREEN]** Create backend/src/study_helper/schemas/task.py with TaskCreate schema
- [x] T126 [P] [US1] **[GREEN]** Implement auto-title logic: if title empty, generate "Untitled Task - {timestamp}"
- [x] T127 [P] [US1] **[GREEN]** Create TaskUpdate schema (all fields optional + is_completed)
- [x] T128 [P] [US1] **[GREEN]** Create TaskResponse schema with subtasks array and linked_notes_count

**TDD: Task Service**:
- [x] T129 [US1] **[RED]** Create backend/tests/integration/test_task_service.py with test_create_task()
- [x] T130 [US1] **[RED]** Write test_get_tasks_by_course_sorted_oldest_first() (FR-029 default sort)
- [x] T131 [US1] **[RED]** Write test_mark_task_complete_sets_completed_at()
- [x] T132 [US1] **[RED]** Write test_delete_task_succeeds()
- [x] T133 [US1] **[GREEN]** Create backend/src/study_helper/services/task.py with create_task() function
- [x] T134 [US1] **[GREEN]** Implement get_tasks_by_course(course_id, completed, sort_by) with created_at asc default
- [x] T135 [US1] **[GREEN]** Implement update_task() with completed_at timestamp logic
- [x] T136 [US1] **[GREEN]** Implement delete_task() (defer subtask promotion to US4)
- [x] T137 [US1] **[REFACTOR]** Add validation for due_date must be future date when set

**TDD: Task API**:
- [x] T138 [US1] **[RED]** Create backend/tests/contract/test_tasks_api.py with test_create_task_success()
- [x] T139 [US1] **[RED]** Write test_get_tasks_by_course_returns_correct_tasks()
- [x] T140 [US1] **[RED]** Write test_mark_task_complete_via_patch()
- [x] T141 [US1] **[RED]** Write test_delete_task_returns_204()
- [x] T142 [US1] **[GREEN]** Create backend/src/study_helper/api/tasks.py with POST /api/v1/tasks endpoint
- [x] T143 [US1] **[GREEN]** Implement GET /api/v1/courses/{course_id}/tasks with completed and sort_by params
- [x] T144 [US1] **[GREEN]** Implement PATCH /api/v1/tasks/{task_id} endpoint
- [x] T145 [US1] **[GREEN]** Implement DELETE /api/v1/tasks/{task_id} endpoint
- [x] T146 [US1] **[GREEN]** Add tasks router to main.py

### Frontend (US1 - Basic UI)

- [X] T147 [P] [US1] Create frontend/src/index.html with semantic HTML5 structure
- [X] T148 [P] [US1] Create frontend/src/css/main.css with Tailwind CDN link
- [X] T149 [P] [US1] Create frontend/src/js/api/client.js with base HTTP client and JWT token injection
- [X] T150 [P] [US1] Create frontend/src/js/api/auth.js with register() and login() functions
- [X] T151 [P] [US1] Create frontend/src/js/api/courses.js with CRUD functions for courses
- [X] T152 [P] [US1] Create frontend/src/js/api/notes.js with CRUD functions for notes
- [X] T153 [P] [US1] Create frontend/src/js/api/tasks.js with CRUD functions for tasks
- [X] T154 [US1] Create frontend/src/js/components/course-list.js rendering courses with create/archive UI
- [X] T155 [US1] Create frontend/src/js/components/note-editor.js with contenteditable and Markdown storage
- [X] T156 [US1] Create frontend/src/js/components/task-list.js with task CRUD and completion toggle
- [X] T157 [US1] Create frontend/src/js/main.js with app initialization and auth check
- [X] T158 [US1] Add LocalStorage for offline queue (queue failed API requests)
- [X] T159 [US1] Verify <2s page load and <100ms UI interactions with Chrome DevTools

**US1 Success Criteria**:
- ✅ Users can register and login
- ✅ Users can create courses and see them listed
- ✅ Users can create notes in a course and edit them
- ✅ Users can create tasks with due dates
- ✅ Users can mark tasks as complete
- ✅ 90% test coverage for CRUD services (constitution requirement)

---

## Phase 4: User Story 2 [P2] - Unified Task View

**Goal**: Students view tasks by time period (Today, This Week, Upcoming) across all courses  
**Independent Test**: Create tasks with different dates → verify Today/Week/Upcoming views filter correctly  
**Reference**: [spec.md US2](./spec.md#user-story-2---unified-task-view-and-time-management-priority-p2)

### Date Filtering Utilities (US2)

**TDD: Date Filters**:
- [X] T160 [P] [US2] **[RED]** Create backend/tests/unit/test_date_filters.py with test_is_today()
- [X] T161 [P] [US2] **[RED]** Write test_is_this_week_includes_today() (Clarification #4)
- [X] T162 [P] [US2] **[RED]** Write test_is_upcoming_beyond_7_days()
- [X] T163 [P] [US2] **[GREEN]** Create backend/src/study_helper/utils/date_filters.py with is_today() function
- [X] T164 [P] [US2] **[GREEN]** Implement is_this_week() returning true for today through next 7 days
- [X] T165 [P] [US2] **[GREEN]** Implement is_upcoming() returning true for beyond this week
- [X] T166 [P] [US2] **[REFACTOR]** Add timezone handling (use UTC for consistency)

### Task Service Extension (US2)

**TDD: Time-Based Views**:
- [X] T167 [US2] **[RED]** Write test_get_tasks_today_view() in backend/tests/integration/test_task_service.py
- [X] T168 [US2] **[RED]** Write test_get_tasks_this_week_view_includes_today()
- [X] T169 [US2] **[RED]** Write test_get_tasks_upcoming_view()
- [X] T170 [US2] **[RED]** Write test_tasks_without_due_date_appear_in_no_due_date_section()
- [X] T171 [US2] **[GREEN]** Extend get_tasks_by_course() with view parameter (all, today, week, upcoming)
- [X] T172 [US2] **[GREEN]** Implement filter logic using date_filters.py functions
- [X] T173 [US2] **[GREEN]** Add grouping by due_date for "This Week" view
- [X] T174 [US2] **[REFACTOR]** Optimize query with indexes on (course_id, due_date)

### Task API Extension (US2)

**TDD: View Endpoints**:
- [X] T175 [US2] **[RED]** Write test_get_tasks_today_view_returns_only_today() in backend/tests/contract/test_tasks_api.py
- [X] T176 [US2] **[RED]** Write test_get_tasks_week_view_aggregates_across_courses()
- [X] T177 [US2] **[RED]** Write test_get_tasks_upcoming_view_sorted_by_date()
- [X] T178 [US2] **[GREEN]** Update GET /api/v1/courses/{course_id}/tasks to accept view=today|week|upcoming
- [X] T179 [US2] **[GREEN]** Add GET /api/v1/tasks/today endpoint (all courses, today's tasks)
- [X] T180 [US2] **[GREEN]** Add GET /api/v1/tasks/week endpoint (all courses, this week's tasks)
- [X] T181 [US2] **[GREEN]** Add GET /api/v1/tasks/upcoming endpoint (all courses, upcoming tasks)

### Frontend (US2 - Task Views)

- [X] T182 [P] [US2] Create frontend/src/js/components/task-views.js with Today/Week/Upcoming tabs
- [X] T183 [P] [US2] Implement tab switching logic with active state styling
- [X] T184 [P] [US2] Add visual indication for overdue tasks (red text, warning icon)
- [X] T185 [P] [US2] Implement "No Due Date" section for tasks without due_date
- [X] T186 [US2] Add priority sorting within each date group (high → medium → low)
- [X] T187 [US2] Verify <100ms tab switching performance

**US2 Success Criteria**:
- ✅ Today view shows only today's tasks
- ✅ This Week view includes today + next 7 days
- ✅ Upcoming view shows tasks beyond this week
- ✅ Tasks grouped by due date in Week view
- ✅ Overdue tasks visually indicated

---

## Phase 5: User Story 3 [P3] - Link Tasks to Notes

**Goal**: Students link tasks to notes, creating bidirectional references  
**Independent Test**: Create note → create task → link them → verify link visible from both sides  
**Reference**: [spec.md US3](./spec.md#user-story-3---link-tasks-to-notes-priority-p3)

### NoteTaskLink Model (US3)

**TDD: Many-to-Many Relationship**:
- [ ] T188 [P] [US3] **[RED]** Write test_note_task_link_creation() in backend/tests/unit/test_models.py
- [ ] T189 [P] [US3] **[RED]** Write test_note_task_link_unique_constraint()
- [ ] T190 [P] [US3] **[GREEN]** Create backend/src/study_helper/models/note_task_link.py per data-model.md § 2.5
- [ ] T191 [P] [US3] **[GREEN]** Add composite primary key (note_id, task_id)
- [ ] T192 [P] [US3] **[GREEN]** Add unique constraint on (note_id, task_id)
- [ ] T193 [P] [US3] **[GREEN]** Run migration: `alembic revision --autogenerate -m "Add NoteTaskLink table"`

### Service Layer (US3)

**TDD: Linking Logic**:
- [ ] T194 [US3] **[RED]** Write test_link_note_to_task() in backend/tests/integration/test_note_service.py
- [ ] T195 [US3] **[RED]** Write test_link_note_to_task_duplicate_fails()
- [ ] T196 [US3] **[RED]** Write test_unlink_note_from_task()
- [ ] T197 [US3] **[RED]** Write test_delete_note_removes_links_keeps_tasks()
- [ ] T198 [US3] **[GREEN]** Add link_note_to_task(note_id, task_id) function to note.py service
- [ ] T199 [US3] **[GREEN]** Add unlink_note_from_task(note_id, task_id) function
- [ ] T200 [US3] **[GREEN]** Update get_notes_by_course() to include linked_tasks in response
- [ ] T201 [US3] **[GREEN]** Update get_tasks_by_course() to include linked_notes_count in response
- [ ] T202 [US3] **[REFACTOR]** Use SQLAlchemy selectinload() to prevent N+1 queries on links

### API Endpoints (US3)

**TDD: Link Endpoints**:
- [ ] T203 [US3] **[RED]** Write test_link_note_to_task_success() in backend/tests/contract/test_notes_api.py
- [ ] T204 [US3] **[RED]** Write test_link_note_to_task_duplicate_returns_409()
- [ ] T205 [US3] **[RED]** Write test_unlink_note_from_task_returns_204()
- [ ] T206 [US3] **[GREEN]** Add POST /api/v1/notes/{note_id}/link-task endpoint
- [ ] T207 [US3] **[GREEN]** Add DELETE /api/v1/notes/{note_id}/link-task/{task_id} endpoint
- [ ] T208 [US3] **[REFACTOR]** Add 404 handling for non-existent notes or tasks

### Frontend (US3 - Linking UI)

- [ ] T209 [P] [US3] Create frontend/src/js/components/note-task-linker.js with search and select UI
- [ ] T210 [P] [US3] Add "Link to Note" button in task detail view
- [ ] T211 [P] [US3] Show linked notes list in task detail view (clickable to open note)
- [ ] T212 [P] [US3] Show linked tasks list at bottom of note editor
- [ ] T213 [US3] Implement search/filter for notes when linking from task
- [ ] T214 [US3] Add visual indicator (badge/count) showing number of links

**US3 Success Criteria**:
- ✅ Tasks can be linked to multiple notes
- ✅ Notes show all linked tasks
- ✅ Tasks show all linked notes
- ✅ Deleting note removes links but keeps tasks
- ✅ Search/filter works when selecting notes to link

---

## Phase 6: User Story 4 [P4] - Subtasks

**Goal**: Students break down tasks into subtasks with independent completion tracking  
**Independent Test**: Create task → add subtasks → complete subtasks → verify progress indicator  
**Reference**: [spec.md US4](./spec.md#user-story-4---task-breakdown-and-subtasks-priority-p4)

### Subtask Logic (US4)

**TDD: Subtask Relationships**:
- [ ] T215 [P] [US4] **[RED]** Write test_task_subtask_relationship() in backend/tests/unit/test_models.py
- [ ] T216 [P] [US4] **[RED]** Write test_delete_parent_promotes_subtasks() (Clarification #2)
- [ ] T217 [P] [US4] **[RED]** Write test_complete_all_subtasks_marks_parent_complete()
- [ ] T218 [P] [US4] **[GREEN]** Update Task model to use self-referential parent_task_id (already in T120)
- [ ] T219 [P] [US4] **[GREEN]** Add cascade delete logic for subtasks in task.py service
- [ ] T220 [P] [US4] **[REFACTOR]** Verify subtasks relationship uses back_populates correctly

### Service Layer (US4)

**TDD: Subtask Operations**:
- [ ] T221 [US4] **[RED]** Write test_create_subtask() in backend/tests/integration/test_task_service.py
- [ ] T222 [US4] **[RED]** Write test_get_task_with_subtasks_includes_progress()
- [ ] T223 [US4] **[RED]** Write test_delete_parent_task_promotes_subtasks_to_top_level()
- [ ] T224 [US4] **[RED]** Write test_complete_all_subtasks_auto_completes_parent()
- [ ] T225 [US4] **[GREEN]** Add create_subtask(parent_task_id, data) function to task.py service
- [ ] T226 [US4] **[GREEN]** Update delete_task() to set parent_task_id=NULL on all subtasks (promotion)
- [ ] T227 [US4] **[GREEN]** Add auto-complete parent logic when all subtasks completed
- [ ] T228 [US4] **[GREEN]** Add progress calculation (completed_count / total_count)
- [ ] T229 [US4] **[REFACTOR]** Add validation: subtasks can have due_date earlier than parent

### API Endpoints (US4)

**TDD: Subtask Endpoints**:
- [ ] T230 [US4] **[RED]** Write test_create_subtask_success() in backend/tests/contract/test_tasks_api.py
- [ ] T231 [US4] **[RED]** Write test_get_task_includes_subtasks_with_progress()
- [ ] T232 [US4] **[RED]** Write test_delete_parent_promotes_subtasks()
- [ ] T233 [US4] **[GREEN]** Add POST /api/v1/tasks/{task_id}/subtasks endpoint
- [ ] T234 [US4] **[GREEN]** Update GET /api/v1/tasks/{task_id} response to include subtasks array
- [ ] T235 [US4] **[GREEN]** Add progress field to TaskResponse (e.g., "2/5 complete")

### Frontend (US4 - Subtask UI)

- [ ] T236 [P] [US4] Add "Add Subtask" button to task detail view
- [ ] T237 [P] [US4] Render subtasks list with indentation/nesting visual
- [ ] T238 [P] [US4] Show progress indicator (e.g., "2/5 complete") on parent task
- [ ] T239 [P] [US4] Implement drag-to-reorder for subtasks (optional, can defer)
- [ ] T240 [US4] Add confirmation dialog when deleting parent task with subtasks

**US4 Success Criteria**:
- ✅ Tasks can have subtasks
- ✅ Subtasks can be completed independently
- ✅ Progress indicator shows completion status
- ✅ Deleting parent promotes subtasks to top-level
- ✅ Completing all subtasks auto-completes parent

---

## Phase 7: User Story 5 [P5] - Search

**Goal**: Students search across all notes and tasks by keyword  
**Independent Test**: Create diverse notes → search with keywords → verify accurate results with highlighting  
**Reference**: [spec.md US5](./spec.md#user-story-5---search-and-discovery-priority-p5), [data-model.md § 3](./data-model.md#3-full-text-search-fts5)

### FTS5 Setup (US5)

**TDD: Full-Text Search**:
- [ ] T241 [P] [US5] **[RED]** Write test_search_notes_by_keyword() in backend/tests/unit/test_search.py
- [ ] T242 [P] [US5] **[RED]** Write test_search_with_stemming() (e.g., "running" finds "run")
- [ ] T243 [P] [US5] **[RED]** Write test_search_performance_1000_notes() (<1s requirement)
- [ ] T244 [P] [US5] **[GREEN]** Create backend/src/study_helper/db/fts_setup.py with FTS5 virtual table SQL
- [ ] T245 [P] [US5] **[GREEN]** Create migration with FTS5 table and INSERT/UPDATE/DELETE triggers
- [ ] T246 [P] [US5] **[GREEN]** Run migration: `alembic revision -m "Add FTS5 search for notes"`
- [ ] T247 [P] [US5] **[REFACTOR]** Verify Porter stemming tokenizer configured correctly

### Search Service (US5)

**TDD: Search Logic**:
- [ ] T248 [US5] **[RED]** Write test_search_notes_returns_ranked_results() in backend/tests/integration/test_search_service.py
- [ ] T249 [US5] **[RED]** Write test_search_filters_by_user_id() (security: users only see their notes)
- [ ] T250 [US5] **[RED]** Write test_search_includes_snippet_highlighting()
- [ ] T251 [US5] **[GREEN]** Create backend/src/study_helper/services/search.py with search_notes() function
- [ ] T252 [US5] **[GREEN]** Implement FTS5 MATCH query with BM25 ranking
- [ ] T253 [US5] **[GREEN]** Add user_id filter via JOIN through course → user
- [ ] T254 [US5] **[GREEN]** Add snippet extraction with keyword highlighting
- [ ] T255 [US5] **[REFACTOR]** Add pagination (limit 50 default, max 100)

### Search API (US5)

**TDD: Search Endpoint**:
- [ ] T256 [US5] **[RED]** Write test_search_endpoint_success() in backend/tests/contract/test_search_api.py
- [ ] T257 [US5] **[RED]** Write test_search_requires_authentication()
- [ ] T258 [US5] **[RED]** Write test_search_latency_under_1_second() (benchmark test)
- [ ] T259 [US5] **[GREEN]** Create backend/src/study_helper/api/search.py with GET /api/v1/search endpoint
- [ ] T260 [US5] **[GREEN]** Add query parameter q (required) and limit (optional, default 50)
- [ ] T261 [US5] **[GREEN]** Return results with rank, snippet, and note metadata
- [ ] T262 [US5] **[REFACTOR]** Add error handling for empty query (400 Bad Request)

### Frontend (US5 - Search UI)

- [ ] T263 [P] [US5] Create frontend/src/js/components/search-bar.js with search input and results dropdown
- [ ] T264 [P] [US5] Implement debounced search (300ms delay after typing stops)
- [ ] T265 [P] [US5] Render search results with keyword highlighting in snippets
- [ ] T266 [P] [US5] Add "No results found" message with suggestions
- [ ] T267 [US5] Implement keyboard navigation (arrow keys to navigate results, Enter to open)
- [ ] T268 [US5] Add search result filtering by course (optional)

**US5 Success Criteria**:
- ✅ Search finds notes by title and content
- ✅ Porter stemming works (e.g., "studying" finds "study")
- ✅ Results ranked by relevance (BM25)
- ✅ Keyword highlighting in result snippets
- ✅ Search completes in <1s for 1000 notes (constitution requirement)

---

## Phase 8: User Story 6 [P6] - Inbox (Optional)

**Goal**: Students quickly capture items to Inbox for later organization  
**Independent Test**: Quick add to inbox → view inbox → assign to course → verify moved out of inbox  
**Reference**: [spec.md US6](./spec.md#user-story-6---inbox-and-quick-entry-priority-p6)

### Inbox Model (US6)

**TDD: Inbox Flag**:
- [ ] T269 [P] [US6] **[RED]** Write test_note_inbox_flag() in backend/tests/unit/test_models.py
- [ ] T270 [P] [US6] **[RED]** Write test_task_inbox_flag()
- [ ] T271 [P] [US6] **[GREEN]** Add is_inbox boolean field to Note model (default False)
- [ ] T272 [P] [US6] **[GREEN]** Add is_inbox boolean field to Task model (default False)
- [ ] T273 [P] [US6] **[GREEN]** Run migration: `alembic revision --autogenerate -m "Add inbox flags"`
- [ ] T274 [P] [US6] **[REFACTOR]** Add index on is_inbox for inbox view query performance

### Service Layer (US6)

**TDD: Inbox Operations**:
- [ ] T275 [US6] **[RED]** Write test_create_note_in_inbox() in backend/tests/integration/test_note_service.py
- [ ] T276 [US6] **[RED]** Write test_get_inbox_items()
- [ ] T277 [US6] **[RED]** Write test_move_note_from_inbox_to_course()
- [ ] T278 [US6] **[GREEN]** Update create_note() to accept is_inbox parameter (course_id optional if inbox)
- [ ] T279 [US6] **[GREEN]** Add get_inbox_items(user_id) function returning all inbox notes and tasks
- [ ] T280 [US6] **[GREEN]** Update update_note() to move from inbox (set is_inbox=False, course_id=X)
- [ ] T281 [US6] **[REFACTOR]** Add created_at sorting for inbox (oldest first for processing)

### API Endpoints (US6)

**TDD: Inbox Endpoints**:
- [ ] T282 [US6] **[RED]** Write test_quick_add_to_inbox() in backend/tests/contract/test_inbox_api.py
- [ ] T283 [US6] **[RED]** Write test_get_inbox_items()
- [ ] T284 [US6] **[RED]** Write test_move_item_from_inbox_to_course()
- [ ] T285 [US6] **[GREEN]** Add POST /api/v1/inbox endpoint (quick add with is_inbox=True)
- [ ] T286 [US6] **[GREEN]** Add GET /api/v1/inbox endpoint (return all inbox items)
- [ ] T287 [US6] **[GREEN]** Update PATCH /api/v1/notes/{id} to handle inbox → course migration

### Frontend (US6 - Inbox UI)

- [ ] T288 [P] [US6] Create frontend/src/js/components/inbox.js with inbox view
- [ ] T289 [P] [US6] Add "Quick Add" button in header (keyboard shortcut: Ctrl+N)
- [ ] T290 [P] [US6] Show time since creation (e.g., "3 days ago") for inbox items
- [ ] T291 [P] [US6] Implement drag-to-assign (drag inbox item to course to move)
- [ ] T292 [US6] Add badge showing inbox count in navigation

**US6 Success Criteria**:
- ✅ Quick add creates item in inbox (<3s on mobile)
- ✅ Inbox view shows all unorganized items
- ✅ Items can be moved from inbox to course
- ✅ Time since creation displayed

---

## Phase 9: User Story 7 [P7] - Notifications (Optional)

**Goal**: Students receive reminders about upcoming and overdue tasks  
**Independent Test**: Create task with due date → configure notifications → verify notification appears  
**Reference**: [spec.md US7](./spec.md#user-story-7---reminders-and-notifications-priority-p7)

### Notification Preferences (US7)

**TDD: User Preferences**:
- [ ] T293 [P] [US7] **[RED]** Write test_user_notification_preferences() in backend/tests/unit/test_models.py
- [ ] T294 [P] [US7] **[GREEN]** Add notification_settings JSON field to User model
- [ ] T295 [P] [US7] **[GREEN]** Create NotificationSettings schema (timing, enabled_courses)
- [ ] T296 [P] [US7] **[GREEN]** Run migration: `alembic revision --autogenerate -m "Add notification settings"`

### Notification Service (US7)

**TDD: Notification Logic**:
- [ ] T297 [US7] **[RED]** Write test_get_upcoming_task_notifications() in backend/tests/integration/test_notification_service.py
- [ ] T298 [US7] **[RED]** Write test_overdue_task_notifications()
- [ ] T299 [US7] **[RED]** Write test_completed_task_skips_notification()
- [ ] T300 [US7] **[GREEN]** Create backend/src/study_helper/services/notification.py
- [ ] T301 [US7] **[GREEN]** Implement get_pending_notifications(user_id) function
- [ ] T302 [US7] **[GREEN]** Add filter for completed tasks (skip notifications)
- [ ] T303 [US7] **[GREEN]** Add course-level notification filtering (respect user preferences)

### API Endpoints (US7)

**TDD: Notification Endpoints**:
- [ ] T304 [US7] **[RED]** Write test_get_notifications() in backend/tests/contract/test_notification_api.py
- [ ] T305 [US7] **[RED]** Write test_update_notification_settings()
- [ ] T306 [US7] **[GREEN]** Add GET /api/v1/notifications endpoint (pending notifications)
- [ ] T307 [US7] **[GREEN]** Add PATCH /api/v1/users/me/notification-settings endpoint
- [ ] T308 [US7] **[GREEN]** Add GET /api/v1/notifications/daily-summary endpoint (morning summary)

### Frontend (US7 - Notifications UI)

- [ ] T309 [P] [US7] Create frontend/src/js/components/notification-banner.js for overdue tasks
- [ ] T310 [P] [US7] Add notification settings page (timing, per-course toggles)
- [ ] T311 [P] [US7] Implement browser push notifications (if supported)
- [ ] T312 [P] [US7] Show morning summary modal on app open (if tasks due today)
- [ ] T313 [US7] Add notification badge in header showing count

**US7 Success Criteria**:
- ✅ Notifications appear for upcoming tasks (configurable timing)
- ✅ Overdue banner shows when tasks are overdue
- ✅ Users can customize notification preferences
- ✅ Morning summary shows today's tasks
- ✅ Completed tasks skip notifications

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Performance optimization, UX polish, accessibility, deployment readiness  
**Reference**: Constitution Principle III (UX) and IV (Performance)

### Performance Optimization

- [ ] T314 [P] Verify all database indexes from data-model.md § 4 exist
- [ ] T315 [P] Add SQLAlchemy selectinload() to prevent N+1 queries on relationships
- [ ] T316 [P] Implement pagination for all list endpoints (limit 50 default)
- [ ] T317 [P] Add response compression middleware in main.py
- [ ] T318 Create backend/src/study_helper/middleware/timing.py logging response times
- [ ] T319 Run pytest-benchmark tests verifying <200ms P95 API latency
- [ ] T320 Run search performance test verifying <1s for 1000 notes

### Frontend Performance

- [ ] T321 [P] Implement lazy loading for notes and tasks (pagination)
- [ ] T322 [P] Add debouncing (300ms) to search input
- [ ] T323 [P] Cache course list in LocalStorage (invalidate on changes)
- [ ] T324 [P] Optimize Tailwind CSS (custom build instead of CDN for production)
- [ ] T325 Run Chrome DevTools Lighthouse audit (target 90+ performance score)
- [ ] T326 Verify <2s page load and <100ms UI interactions

### Accessibility (WCAG 2.1 AA)

- [ ] T327 [P] Add ARIA labels to all interactive elements (buttons, inputs, links)
- [ ] T328 [P] Implement keyboard navigation (Tab, Enter, Esc, arrow keys)
- [ ] T329 [P] Verify 4.5:1 color contrast ratio on all text (use WebAIM contrast checker)
- [ ] T330 [P] Add focus indicators (visible outline on keyboard focus)
- [ ] T331 [P] Test screen reader compatibility (NVDA or JAWS)
- [ ] T332 Add skip-to-content link for keyboard users
- [ ] T333 Ensure all form inputs have associated labels

### UX Consistency

- [ ] T334 [P] Create frontend/src/css/design-system.css with Tailwind custom theme
- [ ] T335 [P] Define color palette for course colors, task priorities, and status
- [ ] T336 [P] Add loading states (skeleton screens for lists, spinners for >500ms operations)
- [ ] T337 [P] Implement toast notifications for user feedback (success, error, info)
- [ ] T338 [P] Add confirmation dialogs for destructive actions (delete course, delete task with subtasks)
- [ ] T339 Create error message guidelines document (user-friendly with next steps)
- [ ] T340 Implement optimistic UI updates (instant feedback, rollback on error)

### Error Handling

- [ ] T341 [P] Create backend/src/study_helper/core/exceptions.py with custom exception classes
- [ ] T342 [P] Add FastAPI exception handlers for 400, 401, 403, 404, 409, 500
- [ ] T343 [P] Implement structured error response format per api-specification.md
- [ ] T344 [P] Add logging with context (user_id, request_id, timestamp)
- [ ] T345 Add error boundary in frontend (catch JS errors, show friendly message)
- [ ] T346 Implement retry logic for failed API requests in offline queue

### Offline Sync

- [ ] T347 [P] Implement Last-Write-Wins conflict resolution per research.md § 5
- [ ] T348 [P] Create backend/src/study_helper/services/sync.py with sync_changes() function
- [ ] T349 [P] Add POST /api/v1/sync endpoint per api-specification.md
- [ ] T350 Create frontend/src/js/utils/sync.js with online/offline detection
- [ ] T351 Implement LocalStorage queue for offline changes
- [ ] T352 Add toast notification for sync conflicts (server wins, user informed)
- [ ] T353 Write test_conflict_resolution_server_wins() in backend/tests/integration/test_offline_sync.py

### Documentation

- [ ] T354 [P] Create backend/README.md with setup and development instructions
- [ ] T355 [P] Create frontend/README.md with build and deployment instructions
- [ ] T356 [P] Document API at /docs (auto-generated by FastAPI)
- [ ] T357 [P] Create CONTRIBUTING.md with code style guide and PR process
- [ ] T358 Add inline code comments for complex business logic
- [ ] T359 Create deployment guide (Docker, environment variables, database migrations)

### Testing

- [ ] T360 Run full test suite: `uv run pytest`
- [ ] T361 Verify 100% coverage for auth, date filtering, note-task linking (constitution)
- [ ] T362 Verify 90% coverage for CRUD services (constitution)
- [ ] T363 Verify 80% overall coverage (constitution)
- [ ] T364 Run mypy type checking: `uv run mypy src/study_helper`
- [ ] T365 Run linting: `uv run ruff check src tests`
- [ ] T366 Run formatting: `uv run black src tests --check`

### Deployment Preparation

- [ ] T367 [P] Create Dockerfile for backend with multi-stage build
- [ ] T368 [P] Create docker-compose.yml for local development (backend + frontend)
- [ ] T369 [P] Configure environment variables for production (SECRET_KEY, DATABASE_URL)
- [ ] T370 [P] Set up Alembic migration strategy for production (backup before upgrade)
- [ ] T371 Create frontend build script (Tailwind CSS compilation, minification)
- [ ] T372 Add health check endpoint: GET /health (return 200 if database accessible)
- [ ] T373 Create deployment checklist (migrations, environment vars, static files)

---

## Constitution Compliance Checklist

**Before merging to master, verify ALL gates pass:**

### Code Quality (Principle I)
- [ ] All functions have single responsibility
- [ ] Type hints on all functions (mypy passes with zero errors)
- [ ] No code duplication (DRY principle enforced)
- [ ] Error handling with structured responses (FastAPI exception handlers)

### Test-First (Principle II)
- [ ] 100% coverage: auth (T015-T050), date filtering (T160-T166), note-task linking (T188-T208)
- [ ] 90% coverage: CRUD services (courses, notes, tasks)
- [ ] 80% overall coverage (run `pytest --cov`)
- [ ] All tests pass (`uv run pytest`)

### UX Consistency (Principle III)
- [ ] Tailwind design system used throughout (T334-T335)
- [ ] WCAG 2.1 AA compliance (T327-T333)
- [ ] User-friendly error messages (T339)
- [ ] Loading states for >500ms operations (T336)

### Performance (Principle IV)
- [ ] <500ms note/task creation (T319)
- [ ] <100ms UI interactions (T326)
- [ ] <200ms P95 API latency (T319)
- [ ] <1s search latency (T320)
- [ ] <2s page load (T325-T326)

---

## Summary

**Total Tasks**: 373  
**Estimated Time**: ~120-150 hours (3-4 weeks for 1 developer, 1.5-2 weeks for 2 developers)

**MVP Scope** (User Story 1): Tasks T001-T159 (~50 hours)
- Project setup + auth + courses + notes + tasks + basic frontend
- Delivers immediate value: students can capture and organize notes/tasks

**Parallel Execution Examples**:
- **Phase 1 (Setup)**: T001-T006 can run in parallel (different files)
- **Phase 2 (Auth)**: T024-T027 (security) parallel with T028-T033 (schemas)
- **Phase 3 (US1)**: T051-T056 (Course model) parallel with T057-T063 (Course schemas)
- **Frontend**: All component files (T147-T159) can be built in parallel

**Incremental Delivery Strategy**:
1. Deploy MVP (US1) after T159 - students can capture notes/tasks
2. Deploy US2 after T187 - adds time-based task views
3. Deploy US3 after T214 - adds note-task linking
4. Deploy US4-US7 as optional enhancements
5. Deploy Phase 10 polish for production readiness

**Next Action**: Start with T001 (uv init project) and follow TDD workflow (Red-Green-Refactor) for each task.
