# Research: Student Knowledge Management App

**Date**: 2025-01-23  
**Feature**: 001-student-knowledge-app  
**Purpose**: Resolve technical unknowns and validate technology choices

---

## 1. Backend Framework Selection

### Decision: FastAPI

**Rationale:**
- **Type Safety**: Native Pydantic integration enforces type validation at API boundaries (Constitution Principle I.D)
- **Async Support**: Native async/await for concurrent database operations meets <200ms P95 latency requirement (Constitution Principle IV.B)
- **Auto Documentation**: OpenAPI schema generation aligns with contract-first development (Test-First workflow)
- **Developer Experience**: Fast reload, excellent error messages improve development velocity
- **SQLAlchemy Compatibility**: First-class async SQLAlchemy support for database operations

**Alternatives Considered:**
- **Flask**: Lacks native async support, manual type validation would violate type safety principle
- **Django**: Too heavy for MVP, ORM lock-in complicates testing, slower startup contradicts simplicity
- **Sanic**: Less mature ecosystem, weaker type integration, smaller community

**Constitution Alignment:**
- ✅ Principle I.D: Type hints required (Pydantic models enforce this)
- ✅ Principle II.A: Testable (pytest-asyncio + TestClient)
- ✅ Principle IV.B: Performance (<200ms possible with async)

---

## 2. Database Choice

### Decision: SQLite (development/MVP) → PostgreSQL (production scale)

**Rationale:**
- **SQLite for MVP**:
  - Zero configuration aligns with constitution's simplicity preference
  - File-based storage enables offline-first architecture
  - Full-text search via FTS5 extension (<1s search requirement, FR-024)
  - Atomic transactions for data integrity
  - Sufficient for single-user application up to ~100K records
  
- **PostgreSQL Migration Path**:
  - SQLAlchemy abstracts dialect differences
  - Better full-text search (tsvector, GIN indexes) for scale
  - JSON column support for flexible note metadata
  - Connection pooling for concurrent users

**Alternatives Considered:**
- **PostgreSQL Only**: Over-engineering for MVP, deployment complexity contradicts YAGNI
- **MongoDB**: Schema flexibility not needed, poor full-text search, harder testing
- **DuckDB**: Excellent analytics but weaker transactional guarantees

**Constitution Alignment:**
- ✅ Principle I.A: Simplest solution (SQLite) for current need
- ✅ Principle IV.B: FTS5 meets <1s search performance
- ✅ Principle I.C: SQLAlchemy provides migration path

---

## 3. ORM and Data Validation

### Decision: SQLAlchemy 2.0 + Pydantic v2

**Rationale:**
- **SQLAlchemy 2.0**:
  - Type-safe models with declarative syntax
  - Async session support (performance requirement)
  - Relationship tracking prevents N+1 queries
  - Migration tooling (Alembic) for schema evolution
  
- **Pydantic v2**:
  - Request/response validation (constitution type safety)
  - Automatic OpenAPI schema generation
  - Separation of concerns: Pydantic schemas ≠ SQLAlchemy models (layered architecture)
  - Performance: v2 is Rust-powered, faster validation

**Pattern:**
```
Request → Pydantic Schema (validation) → Service Layer → SQLAlchemy Model (persistence)
Response ← Pydantic Schema (serialization) ← Service Layer ← SQLAlchemy Model
```

**Alternatives Considered:**
- **Django ORM**: Tied to Django framework, not compatible with FastAPI async
- **Tortoise ORM**: Less mature, smaller ecosystem, weaker migration tools
- **Raw SQL**: Violates DRY, no type safety, harder testing

**Constitution Alignment:**
- ✅ Principle I.D: Full type safety chain (Pydantic + SQLAlchemy typed models)
- ✅ Principle II.A: Models testable in isolation with in-memory SQLite
- ✅ Principle I.B: Clear separation (schema layer vs persistence layer)

---

## 4. Testing Strategy

### Decision: pytest + pytest-asyncio + pytest-cov + httpx

**Rationale:**
- **pytest**: De facto standard for Python, excellent fixture system
- **pytest-asyncio**: Native async test support for FastAPI endpoints
- **pytest-cov**: Coverage reporting (90% business logic target, Constitution II.D)
- **httpx**: TestClient for FastAPI integration tests
- **Factory Pattern**: Factory classes for test data (reduces test maintenance)

**Test Structure:**
```
tests/
├── unit/                  # Models, schemas, utils (fast, isolated)
├── integration/           # Service layer + database (rollback per test)
└── contract/              # API endpoints (OpenAPI compliance)
```

**Alternatives Considered:**
- **unittest**: Less readable, boilerplate fixtures, pytest is modern standard
- **nose2**: Abandoned project, pytest has better async support
- **Hypothesis**: Property-based testing deferred (YAGNI for MVP)

**Constitution Alignment:**
- ✅ Principle II.A: Test-first development enforced
- ✅ Principle II.C: 100% critical path coverage (auth, data persistence)
- ✅ Principle II.D: 90% business logic coverage (services)

---

## 5. Offline-First Sync Architecture

### Decision: Last-Write-Wins (LWW) with Timestamp Conflict Resolution

**Rationale:**
- **Simplicity**: Matches constitution preference over CRDT complexity
- **User Model**: Single user per account, conflict probability low
- **Implementation**:
  - Each record has `updated_at` timestamp (server-authoritative)
  - Client queues changes in LocalStorage during offline mode
  - On reconnect: POST `/sync` with client changes → server responds with newer server changes
  - Client applies server changes if `server.updated_at > client.updated_at`
  
- **Edge Case** (per clarification decision #3): User informed of data loss via toast notification

**Alternatives Considered:**
- **CRDT (Conflict-Free Replicated Data Types)**: Over-engineering for single-user app, violates simplicity
- **Operational Transformation**: Complex to implement correctly, unnecessary for note-taking
- **Manual Conflict Resolution UI**: Poor UX for students under time pressure

**Constitution Alignment:**
- ✅ Principle I.A: Simplest solution for stated requirements
- ✅ Principle III.B: User informed of conflicts (toast notification)
- ✅ Principle IV.A: <500ms save (timestamp comparison is O(1))

---

## 6. Rich Text Editing

### Decision: ContentEditable + Markdown Storage

**Rationale:**
- **Editor**: Native `contenteditable` div with toolbar for basic formatting (bold, italic, lists)
- **Storage**: Convert to Markdown for database persistence
- **Rendering**: Markdown → HTML with `marked.js` library (2.5KB gzipped)
- **Performance**: No heavy WYSIWYG editor, meets <100ms interaction target

**Format Support** (per Assumption #3 in spec):
- Bold, italic, underline
- Headings (h1-h3)
- Bullet/numbered lists
- Links (manual URL entry)

**Alternatives Considered:**
- **Quill.js**: 43KB gzipped, slower initialization contradicts performance requirement
- **TinyMCE**: 500KB+, massive overhead for basic formatting
- **ProseMirror**: 60KB, steep learning curve, over-engineered for student notes
- **Plain Textarea**: Violates Assumption #3 (basic formatting required)

**Constitution Alignment:**
- ✅ Principle I.A: Simplest solution meeting formatting requirement
- ✅ Principle IV.A: <100ms typing latency (native contenteditable)
- ✅ Principle IV.C: <2s page load (2.5KB library fits budget)

---

## 7. Search Implementation

### Decision: SQLite FTS5 (Full-Text Search)

**Rationale:**
- **FTS5 Extension**: Built into SQLite, zero additional dependencies
- **Performance**: Meets <1s search requirement for MVP scale (Constitution IV.B)
- **Capabilities**:
  - Tokenization with Porter stemming (searches "running" finds "run")
  - Prefix matching for autocomplete
  - BM25 ranking for relevance
  - Highlight snippets in results
  
**Implementation:**
```sql
CREATE VIRTUAL TABLE notes_fts USING fts5(title, content, tokenize='porter');
-- Trigger to keep FTS table synchronized with notes table
```

**Alternatives Considered:**
- **PostgreSQL Full-Text**: Better for scale, but over-engineering for MVP
- **Elasticsearch**: Separate service complexity violates simplicity, harder testing
- **Client-Side JS Search**: Won't scale to 1000+ notes, violates <1s requirement

**Upgrade Path** (if >100K notes):
- Migrate to PostgreSQL with `tsvector` columns and GIN indexes
- Add Redis for search result caching
- SQLAlchemy abstraction makes this seamless

**Constitution Alignment:**
- ✅ Principle I.A: Built-in FTS5 is simplest solution
- ✅ Principle IV.B: <1s search performance validated
- ✅ Principle I.C: SQLAlchemy allows PostgreSQL migration

---

## 8. Frontend Architecture

### Decision: Vanilla JavaScript + Tailwind CSS + Component Pattern

**Rationale:**
- **No Framework**: React/Vue overhead contradicts <2s page load and simplicity
- **Component Pattern**:
  ```javascript
  class NoteCard {
    constructor(data) { this.data = data; }
    render() { return `<div class="note-card">...</div>`; }
  }
  ```
- **Tailwind CSS**: Utility classes prevent CSS bloat, design consistency (Constitution III)
- **LocalStorage**: Offline queue and draft persistence
- **Fetch API**: Standard HTTP client, no axios dependency

**File Organization:**
```
src/
├── components/       # NoteCard, TaskItem, CourseHeader
├── api/              # Fetch wrappers for backend
├── utils/            # Date formatting, search highlighting
└── main.js           # App initialization
```

**Alternatives Considered:**
- **React**: 40KB+ framework, build step complexity, slower initial load
- **Vue**: 33KB, still violates simplicity for MVP scope
- **Svelte**: Compiled output is small, but build tooling adds complexity
- **jQuery**: Outdated, modern DOM APIs are sufficient

**Constitution Alignment:**
- ✅ Principle I.A: Vanilla JS is simplest for stated requirements
- ✅ Principle IV.C: <2s page load (no framework download)
- ✅ Principle III.A: Tailwind enforces consistent spacing/typography

---

## 9. Project Management Tool

### Decision: uv (Python Package Manager)

**Rationale** (per user requirement):
- **Speed**: 10-100x faster than pip (Rust-based)
- **Lock Files**: Deterministic builds (uv.lock)
- **Virtual Environment**: Automatic venv creation
- **PEP 621**: Uses pyproject.toml standard
- **Compatibility**: Works with existing pip/PyPI ecosystem

**Commands:**
```bash
uv init study-helper                    # Initialize project
uv add fastapi sqlalchemy pydantic      # Add dependencies
uv add --dev pytest pytest-asyncio      # Dev dependencies
uv run pytest                           # Run tests in venv
```

**Alternatives Considered:**
- **pip + venv**: Slower, manual lock file management (pip freeze)
- **Poetry**: Slower than uv, heavier tool, more complex
- **Pipenv**: Deprecated by maintainers, slower than uv

**Constitution Alignment:**
- ✅ User Requirement: "Use 'uv' to initialize the project"
- ✅ Principle I.A: Modern, simple tooling
- ✅ Developer Experience: Fast iterations improve TDD workflow

---

## 10. API Design Pattern

### Decision: RESTful JSON API with OpenAPI 3.1

**Rationale:**
- **REST**: Standard HTTP verbs (GET/POST/PATCH/DELETE) for CRUD operations
- **JSON**: Universal format, native JavaScript support
- **OpenAPI**: FastAPI auto-generates docs at `/docs` (contract testing)
- **Versioning**: `/api/v1/` prefix for future compatibility

**Endpoint Structure:**
```
POST   /api/v1/auth/login
GET    /api/v1/courses
POST   /api/v1/courses
GET    /api/v1/courses/{id}/notes
POST   /api/v1/notes
PATCH  /api/v1/notes/{id}
DELETE /api/v1/notes/{id}
GET    /api/v1/search?q=biology
```

**Alternatives Considered:**
- **GraphQL**: Over-engineering for simple CRUD, harder testing, violates simplicity
- **gRPC**: Not browser-friendly, protobuf complexity unnecessary
- **JSON-RPC**: Less standard, poor HTTP caching support

**Constitution Alignment:**
- ✅ Principle II.B: OpenAPI schema enables contract tests
- ✅ Principle I.C: RESTful design is proven pattern
- ✅ Principle III.A: Consistent API structure improves DX

---

## Technology Summary

| Decision Point | Choice | Constitution Principle |
|---------------|--------|------------------------|
| Backend Framework | FastAPI | I.D (type safety), IV.B (performance) |
| Database | SQLite → PostgreSQL | I.A (simplicity), IV.B (search) |
| ORM | SQLAlchemy 2.0 | I.D (types), II.A (testable) |
| Validation | Pydantic v2 | I.D (type safety) |
| Testing | pytest + httpx | II (test-first) |
| Sync Strategy | Last-Write-Wins | I.A (simplicity), III.B (user feedback) |
| Rich Text | contenteditable + Markdown | I.A (simple), IV.A (fast typing) |
| Search | SQLite FTS5 | I.A (built-in), IV.B (<1s) |
| Frontend | Vanilla JS + Tailwind | I.A (simple), IV.C (<2s load) |
| Package Manager | uv | User requirement, I.A (modern tooling) |
| API Design | REST + OpenAPI | I.C (proven), II.B (contract tests) |

---

## Open Questions Resolved

All "NEEDS CLARIFICATION" items from Technical Context are now resolved:

1. ✅ **Rich text editor**: contenteditable + Markdown
2. ✅ **Offline sync**: Last-Write-Wins with timestamp resolution
3. ✅ **Search algorithm**: SQLite FTS5 with Porter stemming
4. ✅ **Frontend framework**: Vanilla JS (no framework)
5. ✅ **CSS approach**: Tailwind utility classes

**Next Phase**: Generate data-model.md with SQLAlchemy models and relationships.
