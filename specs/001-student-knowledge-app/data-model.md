# Data Model: Student Knowledge Management App

**Date**: 2025-01-23  
**Feature**: 001-student-knowledge-app  
**Purpose**: Define entities, relationships, and validation rules

---

## 1. Entity Overview

```
┌─────────────┐
│    User     │
└──────┬──────┘
       │ 1:N
       │
┌──────▼──────┐
│   Course    │◄───────────────────┐
└──────┬──────┘                    │
       │ 1:N                       │
       ├──────────┬────────────────┤
       │          │                │
┌──────▼──────┐ ┌─▼──────────┐   │
│    Note     │ │    Task     │   │
└──────┬──────┘ └──────┬──────┘   │
       │               │           │
       │ M:N           │ 1:N       │
       └───────────────┤           │
                       │           │
                  ┌────▼───────┐  │
                  │  Subtask   │  │
                  └────────────┘  │
                                  │
                  ┌───────────────┘
                  │ M:N (note-task links)
```

**Core Entities:**
1. **User**: Authentication and profile
2. **Course**: Organizational container (semester/subject)
3. **Note**: Rich text content with timestamps
4. **Task**: Todo item with due dates and priority
5. **Subtask**: Child task for decomposition
6. **NoteTaskLink**: Many-to-many relationship between notes and tasks

---

## 2. SQLAlchemy Models

### 2.1 User Model

```python
from sqlalchemy import String, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import List

class User(Base):
    __tablename__ = "users"
    
    # Primary Key
    id: Mapped[int] = mapped_column(primary_key=True)
    
    # Attributes
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    courses: Mapped[List["Course"]] = relationship(back_populates="user", cascade="all, delete-orphan")
```

**Validation Rules** (enforced in Pydantic schemas):
- Email: Valid format, max 255 chars
- Password: Min 8 chars, hashed with bcrypt
- Full Name: Max 100 chars, non-empty

**Indexes:**
- `email` (unique): Fast login lookups

---

### 2.2 Course Model

```python
from sqlalchemy import String, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List

class Course(Base):
    __tablename__ = "courses"
    
    # Primary Key
    id: Mapped[int] = mapped_column(primary_key=True)
    
    # Foreign Key
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    
    # Attributes
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    color: Mapped[str] = mapped_column(String(7), default="#3B82F6", nullable=False)  # Hex color
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user: Mapped["User"] = relationship(back_populates="courses")
    notes: Mapped[List["Note"]] = relationship(back_populates="course", cascade="all, delete-orphan")
    tasks: Mapped[List["Task"]] = relationship(back_populates="course", cascade="all, delete-orphan")
```

**Validation Rules:**
- Name: Max 200 chars, non-empty
- Color: Valid hex format (#RRGGBB)
- Description: Optional, max 2000 chars

**Indexes:**
- `user_id` (foreign key): Query user's courses
- Composite `(user_id, is_archived)`: Filter active courses

**Cascade Behavior** (per Clarification #1):
- Delete course → delete all notes and tasks in that course

---

### 2.3 Note Model

```python
from sqlalchemy import String, DateTime, ForeignKey, Text, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List

class Note(Base):
    __tablename__ = "notes"
    
    # Primary Key
    id: Mapped[int] = mapped_column(primary_key=True)
    
    # Foreign Key
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"), nullable=False, index=True)
    
    # Attributes
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)  # Markdown format
    tags: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)  # Comma-separated
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    course: Mapped["Course"] = relationship(back_populates="notes")
    linked_tasks: Mapped[List["Task"]] = relationship(
        secondary="note_task_links",
        back_populates="linked_notes"
    )
    
    # Full-Text Search (see section 3)
    __table_args__ = (
        Index('ix_notes_course_created', 'course_id', 'created_at'),
    )
```

**Validation Rules:**
- Title: Max 300 chars, non-empty
- Content: Markdown format, max 50,000 chars
- Tags: Comma-separated, max 10 tags, each max 30 chars

**Indexes:**
- `course_id`: Query notes by course
- Composite `(course_id, created_at)`: Sort notes in course (FR-016)

**Full-Text Search:**
- Separate FTS5 virtual table (see section 3)

---

### 2.4 Task Model

```python
from sqlalchemy import String, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List
from enum import Enum

class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class Task(Base):
    __tablename__ = "tasks"
    
    # Primary Key
    id: Mapped[int] = mapped_column(primary_key=True)
    
    # Foreign Key
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"), nullable=False, index=True)
    parent_task_id: Mapped[Optional[int]] = mapped_column(ForeignKey("tasks.id"), nullable=True, index=True)
    
    # Attributes
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    due_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, index=True)
    priority: Mapped[TaskPriority] = mapped_column(SQLEnum(TaskPriority), default=TaskPriority.MEDIUM, nullable=False)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    course: Mapped["Course"] = relationship(back_populates="tasks")
    parent_task: Mapped[Optional["Task"]] = relationship(remote_side=[id], back_populates="subtasks")
    subtasks: Mapped[List["Task"]] = relationship(back_populates="parent_task", cascade="all, delete-orphan")
    linked_notes: Mapped[List["Note"]] = relationship(
        secondary="note_task_links",
        back_populates="linked_tasks"
    )
    
    __table_args__ = (
        Index('ix_tasks_course_due', 'course_id', 'due_date'),
        Index('ix_tasks_course_created', 'course_id', 'created_at'),
    )
```

**Validation Rules:**
- Title: Max 300 chars, auto-generated if empty (FR-034)
- Due Date: Optional, must be future date when set
- Priority: Enum (low/medium/high)
- Description: Optional, max 2000 chars

**Indexes:**
- `course_id`: Query tasks by course
- Composite `(course_id, due_date)`: "This Week" view (FR-021)
- Composite `(course_id, created_at)`: Oldest-first sorting (FR-029)
- `parent_task_id`: Query subtasks

**State Transitions:**
- `is_completed=False` → `is_completed=True`: Set `completed_at=now()`
- Delete parent task → cascade delete subtasks (FR-032)

---

### 2.5 NoteTaskLink Model (Association Table)

```python
from sqlalchemy import ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

class NoteTaskLink(Base):
    __tablename__ = "note_task_links"
    
    # Composite Primary Key
    note_id: Mapped[int] = mapped_column(ForeignKey("notes.id"), primary_key=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"), primary_key=True)
    
    # Timestamp
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    
    __table_args__ = (
        UniqueConstraint('note_id', 'task_id', name='uix_note_task'),
    )
```

**Purpose:** Many-to-many relationship between notes and tasks (FR-008)

**Indexes:**
- Composite primary key provides indexes for both directions

---

## 3. Full-Text Search (FTS5)

### FTS Virtual Table

```sql
CREATE VIRTUAL TABLE notes_fts USING fts5(
    note_id UNINDEXED,
    title,
    content,
    tokenize='porter unicode61'
);

-- Triggers to keep FTS synchronized
CREATE TRIGGER notes_fts_insert AFTER INSERT ON notes
BEGIN
    INSERT INTO notes_fts(note_id, title, content)
    VALUES (NEW.id, NEW.title, NEW.content);
END;

CREATE TRIGGER notes_fts_update AFTER UPDATE ON notes
BEGIN
    UPDATE notes_fts
    SET title = NEW.title, content = NEW.content
    WHERE note_id = NEW.id;
END;

CREATE TRIGGER notes_fts_delete AFTER DELETE ON notes
BEGIN
    DELETE FROM notes_fts WHERE note_id = OLD.id;
END;
```

**Search Query:**
```sql
SELECT notes.* FROM notes
JOIN notes_fts ON notes.id = notes_fts.note_id
WHERE notes_fts MATCH :query
ORDER BY rank
LIMIT 50;
```

**Features:**
- Porter stemming (search "studying" finds "study")
- Prefix matching for autocomplete
- BM25 ranking for relevance
- Meets <1s search performance (FR-024)

---

## 4. Database Indexes Strategy

### Performance Optimization

| Index | Purpose | Requirement |
|-------|---------|-------------|
| `users.email` (unique) | Login lookups | <200ms API (IV.B) |
| `courses.user_id` | User's courses query | FR-011 |
| `courses(user_id, is_archived)` | Active courses filter | FR-012 |
| `notes.course_id` | Notes in course | FR-013 |
| `notes(course_id, created_at)` | Sorted notes list | FR-016 |
| `tasks.course_id` | Tasks in course | FR-018 |
| `tasks(course_id, due_date)` | "This Week" view | FR-021 |
| `tasks(course_id, created_at)` | Oldest-first sorting | FR-029 |
| `tasks.parent_task_id` | Subtask queries | FR-005 |
| `notes_fts` (FTS5) | Full-text search | FR-024 (<1s) |

**Index Maintenance:**
- SQLAlchemy migrations (Alembic) handle index creation
- FTS triggers maintain search index automatically

---

## 5. Data Validation Summary

### Field Constraints

| Entity | Field | Type | Constraints |
|--------|-------|------|-------------|
| User | email | String(255) | Unique, valid format, indexed |
| User | password | String(255) | Min 8 chars (hashed) |
| Course | name | String(200) | Non-empty |
| Course | color | String(7) | Hex format `#RRGGBB` |
| Note | title | String(300) | Non-empty |
| Note | content | Text | Markdown, max 50K chars |
| Note | tags | String(500) | Max 10 tags, comma-separated |
| Task | title | String(300) | Auto-generated if empty (FR-034) |
| Task | priority | Enum | low/medium/high |
| Task | due_date | DateTime | Optional, future date |

### Business Rules

1. **Course Deletion** (Clarification #1):
   - Cascade delete all notes and tasks
   - Confirmation required in UI

2. **Task Completion** (FR-006):
   - Parent task incomplete → all subtasks incomplete
   - Completing parent → option to complete all subtasks

3. **Subtask Promotion** (Clarification #2):
   - Delete parent task → subtasks become top-level tasks
   - Set `parent_task_id = NULL`

4. **Empty Task Titles** (Clarification #5):
   - Auto-generate: "Untitled Task - {timestamp}"
   - Format: "Untitled Task - Jan 23, 2025 3:45 PM"

5. **Offline Sync** (Clarification #3):
   - Last-Write-Wins: `updated_at` timestamp comparison
   - Server timestamp is authoritative

---

## 6. Migration Strategy

### Alembic Workflow

```bash
# Generate migration
uv run alembic revision --autogenerate -m "Initial schema"

# Apply migration
uv run alembic upgrade head

# Rollback
uv run alembic downgrade -1
```

**Initial Migration Checklist:**
1. Create `users` table
2. Create `courses` table with foreign key to users
3. Create `notes` table with foreign key to courses
4. Create `tasks` table with self-referential foreign key and course foreign key
5. Create `note_task_links` association table
6. Create `notes_fts` virtual table with triggers
7. Create all indexes listed in section 4

---

## 7. Sample Data Structure

### Typical User Scenario

```
User: alice@college.edu
├── Course: Biology 101 (#10B981)
│   ├── Note: "Cell Division Lecture" (Jan 15)
│   │   └── Linked to Task: "Study for midterm"
│   ├── Note: "Photosynthesis Lab Notes" (Jan 18)
│   └── Task: "Study for midterm" (Due: Jan 30, Priority: HIGH)
│       ├── Subtask: "Review cell division" (complete)
│       └── Subtask: "Memorize photosynthesis stages"
├── Course: History 202 (#EF4444)
│   ├── Note: "WWI Causes" (Jan 12)
│   └── Task: "Essay on WWI" (Due: Feb 5, Priority: MEDIUM)
└── Course: Math 150 (#F59E0B)
    ├── Note: "Calculus Derivatives" (Jan 10)
    └── Task: "Homework Set 5" (Due: Jan 25, Priority: LOW)
```

**Database Records:**
- 1 user, 3 courses, 4 notes, 4 tasks (1 parent + 2 subtasks + 1 standalone)
- 1 note-task link (Biology note → midterm task)

---

## Next Steps

**Phase 1 Continuation:**
1. Generate API contracts in `/contracts/` (OpenAPI schemas)
2. Create `quickstart.md` with uv setup instructions
3. Update agent context with new technologies

**Phase 2 (via /speckit.tasks):**
1. Implement SQLAlchemy models with type hints
2. Write Alembic migrations
3. Create Pydantic schemas for validation
4. Build service layer with business logic
5. Implement FastAPI endpoints
6. Write pytest tests (unit → integration → contract)
