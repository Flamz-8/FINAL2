# API Contracts: Student Knowledge Management App

**Date**: 2025-01-23  
**Feature**: 001-student-knowledge-app  
**API Version**: v1  
**Base URL**: `/api/v1`

---

## Authentication Endpoints

### POST /api/v1/auth/register

**Purpose**: Create new user account (FR-001)

**Request:**
```json
{
  "email": "alice@college.edu",
  "password": "SecurePass123!",
  "full_name": "Alice Johnson"
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "email": "alice@college.edu",
  "full_name": "Alice Johnson",
  "created_at": "2025-01-23T10:30:00Z"
}
```

**Errors:**
- `400 Bad Request`: Invalid email format, password too short
- `409 Conflict`: Email already registered

---

### POST /api/v1/auth/login

**Purpose**: Authenticate user and receive access token (FR-002)

**Request:**
```json
{
  "email": "alice@college.edu",
  "password": "SecurePass123!"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "alice@college.edu",
    "full_name": "Alice Johnson"
  }
}
```

**Errors:**
- `401 Unauthorized`: Invalid credentials
- `403 Forbidden`: Account disabled

---

## Course Endpoints

### GET /api/v1/courses

**Purpose**: List all courses for authenticated user (FR-011)

**Headers:**
```
Authorization: Bearer {access_token}
```

**Query Parameters:**
- `is_archived` (optional, boolean): Filter by archive status

**Response (200 OK):**
```json
{
  "courses": [
    {
      "id": 1,
      "name": "Biology 101",
      "description": "Introduction to cellular biology",
      "color": "#10B981",
      "is_archived": false,
      "created_at": "2025-01-10T08:00:00Z",
      "updated_at": "2025-01-10T08:00:00Z",
      "notes_count": 5,
      "tasks_count": 3
    },
    {
      "id": 2,
      "name": "History 202",
      "description": null,
      "color": "#EF4444",
      "is_archived": false,
      "created_at": "2025-01-11T09:15:00Z",
      "updated_at": "2025-01-11T09:15:00Z",
      "notes_count": 2,
      "tasks_count": 1
    }
  ],
  "total": 2
}
```

---

### POST /api/v1/courses

**Purpose**: Create new course (FR-003)

**Request:**
```json
{
  "name": "Math 150",
  "description": "Calculus I",
  "color": "#F59E0B"
}
```

**Response (201 Created):**
```json
{
  "id": 3,
  "name": "Math 150",
  "description": "Calculus I",
  "color": "#F59E0B",
  "is_archived": false,
  "created_at": "2025-01-23T10:45:00Z",
  "updated_at": "2025-01-23T10:45:00Z"
}
```

**Errors:**
- `400 Bad Request`: Invalid color format, name too long
- `401 Unauthorized`: Missing/invalid token

---

### PATCH /api/v1/courses/{course_id}

**Purpose**: Update course details (FR-012)

**Request:**
```json
{
  "name": "Math 150 - Advanced",
  "is_archived": true
}
```

**Response (200 OK):**
```json
{
  "id": 3,
  "name": "Math 150 - Advanced",
  "description": "Calculus I",
  "color": "#F59E0B",
  "is_archived": true,
  "updated_at": "2025-01-23T11:00:00Z"
}
```

**Errors:**
- `404 Not Found`: Course does not exist
- `403 Forbidden`: User does not own this course

---

### DELETE /api/v1/courses/{course_id}

**Purpose**: Delete course and all associated data (FR-012, Clarification #1)

**Response (204 No Content):**
```
(empty body)
```

**Errors:**
- `404 Not Found`: Course does not exist
- `403 Forbidden`: User does not own this course

**Note:** Cascades to delete all notes and tasks in this course.

---

## Note Endpoints

### GET /api/v1/courses/{course_id}/notes

**Purpose**: List all notes in a course (FR-013)

**Query Parameters:**
- `sort_by` (optional): `created_at` (default), `updated_at`, `title`
- `order` (optional): `asc`, `desc` (default per FR-016)

**Response (200 OK):**
```json
{
  "notes": [
    {
      "id": 1,
      "course_id": 1,
      "title": "Cell Division Lecture",
      "content": "# Mitosis\n\n**Prophase**: Chromosomes condense...",
      "tags": "mitosis,cell-cycle,biology",
      "created_at": "2025-01-15T14:30:00Z",
      "updated_at": "2025-01-15T14:30:00Z",
      "linked_tasks": [
        {
          "id": 5,
          "title": "Study for midterm"
        }
      ]
    }
  ],
  "total": 1
}
```

---

### POST /api/v1/notes

**Purpose**: Create new note (FR-004)

**Request:**
```json
{
  "course_id": 1,
  "title": "Photosynthesis Lab",
  "content": "## Light Reactions\n\n- Chloroplast structure\n- **Photosystem II** absorbs light...",
  "tags": "photosynthesis,lab,biology"
}
```

**Response (201 Created):**
```json
{
  "id": 2,
  "course_id": 1,
  "title": "Photosynthesis Lab",
  "content": "## Light Reactions\n\n- Chloroplast structure\n- **Photosystem II** absorbs light...",
  "tags": "photosynthesis,lab,biology",
  "created_at": "2025-01-23T11:15:00Z",
  "updated_at": "2025-01-23T11:15:00Z"
}
```

**Errors:**
- `400 Bad Request`: Missing title, content too long
- `404 Not Found`: Course does not exist

---

### PATCH /api/v1/notes/{note_id}

**Purpose**: Update note content (FR-014)

**Request:**
```json
{
  "title": "Photosynthesis Lab - Updated",
  "content": "## Light Reactions (Revised)\n\n...",
  "tags": "photosynthesis,lab,biology,updated"
}
```

**Response (200 OK):**
```json
{
  "id": 2,
  "title": "Photosynthesis Lab - Updated",
  "updated_at": "2025-01-23T11:30:00Z"
}
```

---

### DELETE /api/v1/notes/{note_id}

**Purpose**: Delete note (FR-015)

**Response (204 No Content):**
```
(empty body)
```

**Note:** Removes all note-task links but does NOT delete linked tasks.

---

### POST /api/v1/notes/{note_id}/link-task

**Purpose**: Link note to task (FR-008)

**Request:**
```json
{
  "task_id": 5
}
```

**Response (200 OK):**
```json
{
  "note_id": 2,
  "task_id": 5,
  "created_at": "2025-01-23T11:45:00Z"
}
```

**Errors:**
- `404 Not Found`: Note or task does not exist
- `409 Conflict`: Link already exists

---

### DELETE /api/v1/notes/{note_id}/link-task/{task_id}

**Purpose**: Remove link between note and task (FR-008)

**Response (204 No Content):**
```
(empty body)
```

---

## Task Endpoints

### GET /api/v1/courses/{course_id}/tasks

**Purpose**: List all tasks in a course (FR-018)

**Query Parameters:**
- `view` (optional): `all` (default), `week` (this week per FR-021)
- `completed` (optional, boolean): Filter by completion status
- `sort_by` (optional): `created_at` (default per FR-029), `due_date`, `priority`
- `order` (optional): `asc` (default per FR-029), `desc`

**Response (200 OK):**
```json
{
  "tasks": [
    {
      "id": 5,
      "course_id": 1,
      "title": "Study for midterm",
      "description": "Review chapters 1-5",
      "due_date": "2025-01-30T23:59:00Z",
      "priority": "high",
      "is_completed": false,
      "completed_at": null,
      "created_at": "2025-01-20T10:00:00Z",
      "updated_at": "2025-01-20T10:00:00Z",
      "subtasks": [
        {
          "id": 6,
          "title": "Review cell division",
          "is_completed": true,
          "completed_at": "2025-01-22T15:30:00Z"
        },
        {
          "id": 7,
          "title": "Memorize photosynthesis stages",
          "is_completed": false,
          "completed_at": null
        }
      ],
      "linked_notes_count": 1
    }
  ],
  "total": 1
}
```

---

### POST /api/v1/tasks

**Purpose**: Create new task (FR-005)

**Request:**
```json
{
  "course_id": 1,
  "title": "Homework Set 6",
  "description": "Problems 1-20 from textbook",
  "due_date": "2025-02-01T23:59:00Z",
  "priority": "medium",
  "parent_task_id": null
}
```

**Response (201 Created):**
```json
{
  "id": 8,
  "course_id": 1,
  "title": "Homework Set 6",
  "description": "Problems 1-20 from textbook",
  "due_date": "2025-02-01T23:59:00Z",
  "priority": "medium",
  "is_completed": false,
  "parent_task_id": null,
  "created_at": "2025-01-23T12:00:00Z",
  "updated_at": "2025-01-23T12:00:00Z"
}
```

**Auto-Generated Title** (FR-034):
```json
{
  "course_id": 1,
  "title": "",  // Empty string
  "due_date": "2025-02-01T23:59:00Z"
}
```
Response:
```json
{
  "id": 9,
  "title": "Untitled Task - Jan 23, 2025 12:05 PM",
  "created_at": "2025-01-23T12:05:00Z"
}
```

---

### PATCH /api/v1/tasks/{task_id}

**Purpose**: Update task (FR-019, FR-020)

**Mark Complete:**
```json
{
  "is_completed": true
}
```

**Response (200 OK):**
```json
{
  "id": 8,
  "is_completed": true,
  "completed_at": "2025-01-23T12:10:00Z",
  "updated_at": "2025-01-23T12:10:00Z"
}
```

**Update Due Date/Priority:**
```json
{
  "due_date": "2025-02-05T23:59:00Z",
  "priority": "high"
}
```

---

### DELETE /api/v1/tasks/{task_id}

**Purpose**: Delete task (FR-020)

**Response (204 No Content):**
```
(empty body)
```

**Behavior (Clarification #2):**
- If task has subtasks → subtasks become top-level tasks (set `parent_task_id = NULL`)
- Removes all note-task links

---

### POST /api/v1/tasks/{task_id}/subtasks

**Purpose**: Add subtask to a task (FR-005)

**Request:**
```json
{
  "title": "Review lecture notes",
  "due_date": null,
  "priority": "medium"
}
```

**Response (201 Created):**
```json
{
  "id": 10,
  "parent_task_id": 5,
  "title": "Review lecture notes",
  "is_completed": false,
  "created_at": "2025-01-23T12:20:00Z"
}
```

---

## Search Endpoint

### GET /api/v1/search

**Purpose**: Full-text search across notes (FR-024)

**Query Parameters:**
- `q` (required): Search query
- `limit` (optional, default 50): Max results

**Request:**
```
GET /api/v1/search?q=photosynthesis&limit=20
```

**Response (200 OK):**
```json
{
  "results": [
    {
      "id": 2,
      "course_id": 1,
      "course_name": "Biology 101",
      "title": "Photosynthesis Lab",
      "snippet": "...chloroplast structure\n- **Photosystem II** absorbs light...",
      "created_at": "2025-01-23T11:15:00Z",
      "rank": 0.95
    }
  ],
  "total": 1,
  "query": "photosynthesis"
}
```

**Performance:** <1s response time (Constitution IV.B)

---

## Sync Endpoint

### POST /api/v1/sync

**Purpose**: Offline sync with conflict resolution (FR-026, FR-027)

**Request:**
```json
{
  "changes": [
    {
      "type": "note",
      "action": "update",
      "id": 2,
      "data": {
        "title": "Photosynthesis Lab - Client Edit",
        "updated_at": "2025-01-23T11:25:00Z"
      }
    },
    {
      "type": "task",
      "action": "create",
      "data": {
        "course_id": 1,
        "title": "New task created offline",
        "created_at": "2025-01-23T11:28:00Z"
      }
    }
  ],
  "last_sync_at": "2025-01-23T11:00:00Z"
}
```

**Response (200 OK):**
```json
{
  "applied": 1,
  "conflicts": [
    {
      "type": "note",
      "id": 2,
      "client_updated_at": "2025-01-23T11:25:00Z",
      "server_updated_at": "2025-01-23T11:30:00Z",
      "resolution": "server_wins",
      "message": "Note was updated on server more recently"
    }
  ],
  "server_changes": [
    {
      "type": "note",
      "action": "update",
      "id": 3,
      "data": {
        "title": "History Essay Notes - Server Edit",
        "updated_at": "2025-01-23T11:35:00Z"
      }
    }
  ],
  "new_sync_timestamp": "2025-01-23T12:30:00Z"
}
```

**Conflict Resolution** (Clarification #3):
- Last-Write-Wins based on `updated_at` timestamp
- Server timestamp is authoritative
- Client informed of conflicts in response

---

## Error Responses

### Standard Error Format

```json
{
  "error": {
    "code": "INVALID_INPUT",
    "message": "Email format is invalid",
    "field": "email"
  }
}
```

### HTTP Status Codes

| Code | Meaning | Example |
|------|---------|---------|
| 200 | OK | Successful GET/PATCH |
| 201 | Created | POST new resource |
| 204 | No Content | DELETE successful |
| 400 | Bad Request | Invalid input data |
| 401 | Unauthorized | Missing/invalid token |
| 403 | Forbidden | User doesn't own resource |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | Duplicate email, link exists |
| 500 | Internal Server Error | Unexpected failure |

---

## Performance Requirements

**Constitution Principle IV.B:**
- All endpoints: <200ms P95 latency
- Search endpoint: <1s P95 latency

**Monitoring:**
- FastAPI middleware logs response times
- Metrics endpoint: `GET /api/v1/metrics` (admin only)

---

## Authentication

**JWT Token Format:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Token Expiration:** 24 hours

**Refresh Flow:** Re-authenticate via `/api/v1/auth/login`

---

## API Versioning

**Current Version:** `v1`

**URL Structure:** `/api/v1/{resource}`

**Future Versions:** `/api/v2/{resource}` (breaking changes only)

---

## Next Steps

1. Implement FastAPI route handlers using these contracts
2. Generate OpenAPI spec automatically via FastAPI
3. Write contract tests using OpenAPI schema validation
4. Create quickstart.md with example curl commands
