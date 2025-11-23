# Study Helper - Backend API

Personal knowledge management app for students to capture notes, manage tasks, and organize study materials.

## Quick Start

### Prerequisites

- Python 3.11+
- uv package manager

### Installation

```powershell
# Navigate to backend directory
cd backend

# Install dependencies
uv sync

# Copy environment file and configure
cp .env.example .env
# Edit .env and set SECRET_KEY to a secure random value
```

### Database Setup

```powershell
# Run database migrations
uv run alembic upgrade head
```

### Run Development Server

```powershell
# Start FastAPI development server
uv run uvicorn src.study_helper.main:app --reload --host 0.0.0.0 --port 8000
```

API will be available at:
- http://localhost:8000
- API docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
backend/
├── src/study_helper/
│   ├── api/          # FastAPI route handlers
│   ├── core/         # Configuration, security
│   ├── db/           # Database setup
│   ├── models/       # SQLAlchemy ORM models
│   ├── schemas/      # Pydantic request/response schemas
│   ├── services/     # Business logic layer
│   └── utils/        # Helper functions
├── tests/
│   ├── unit/         # Unit tests
│   ├── integration/  # Integration tests
│   └── contract/     # API contract tests
└── migrations/       # Alembic database migrations
```

## Development

### Run Tests

```powershell
# Run all tests with coverage
uv run pytest

# Run specific test file
uv run pytest tests/unit/test_models.py

# Run with verbose output
uv run pytest -v
```

### Code Quality

```powershell
# Format code with black
uv run black src tests

# Lint with ruff
uv run ruff check src tests

# Type checking with mypy
uv run mypy src
```

### Create Database Migration

```powershell
# Auto-generate migration from model changes
uv run alembic revision --autogenerate -m "Description of changes"

# Apply migration
uv run alembic upgrade head

# Rollback migration
uv run alembic downgrade -1
```

## Environment Variables

See `.env` file for configuration options:

- `DATABASE_URL`: SQLite database path
- `SECRET_KEY`: JWT signing key (generate with `openssl rand -hex 32`)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: JWT token expiration (default: 1440 = 24 hours)
- `DEBUG`: Enable debug mode (default: False)

## API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Testing

The project follows Test-Driven Development (TDD):
- **100% coverage required**: Authentication, date filtering, note-task linking
- **90% coverage required**: CRUD operations
- **80% overall coverage required**

Run tests before committing:
```powershell
uv run pytest --cov=src/study_helper --cov-report=term-missing
```

## Troubleshooting

### "No module named 'study_helper'"

Make sure you're running commands with `uv run` prefix and that dependencies are installed (`uv sync`).

### Database locked errors

SQLite doesn't handle concurrent writes well. Ensure only one process is accessing the database at a time in development.

### Alembic migration conflicts

```powershell
# Check current migration
uv run alembic current

# Show migration history
uv run alembic history

# Manually resolve conflicts in migrations/versions/
```

## License

MIT
