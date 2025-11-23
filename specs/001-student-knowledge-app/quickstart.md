# Quickstart Guide: Student Knowledge Management App

**Feature**: 001-student-knowledge-app  
**Python Version**: 3.14+  
**Package Manager**: uv  
**Estimated Setup Time**: 10 minutes

---

## Prerequisites

1. **Python 3.14 or higher**
   ```powershell
   python --version  # Should output Python 3.14.x or higher
   ```

2. **uv package manager** (install if needed)
   ```powershell
   # Install uv via pip
   pip install uv
   
   # Verify installation
   uv --version
   ```

3. **Git** (for version control)
   ```powershell
   git --version
   ```

---

## 1. Project Initialization

### Create Project Structure

```powershell
# Navigate to your workspace
cd C:\Users\parth\FINAL2

# Initialize new Python project with uv
uv init study-helper
cd study-helper

# Create directory structure
New-Item -ItemType Directory -Path src/study_helper/{models,schemas,services,api,db,core,utils} -Force
New-Item -ItemType Directory -Path src/{css,js/{components,api,utils}} -Force
New-Item -ItemType Directory -Path tests/{unit,integration,contract} -Force
New-Item -ItemType Directory -Path migrations/versions -Force
New-Item -ItemType Directory -Path static,templates -Force
```

### Configure pyproject.toml

The `uv init` command creates a `pyproject.toml` file. Update it with project dependencies:

```toml
[project]
name = "study-helper"
version = "0.1.0"
description = "Personal knowledge management app for students"
requires-python = ">=3.14"
dependencies = [
    "fastapi>=0.109.0",
    "uvicorn[standard]>=0.27.0",
    "sqlalchemy>=2.0.25",
    "pydantic>=2.5.3",
    "pydantic-settings>=2.1.0",
    "alembic>=1.13.1",
    "python-jose[cryptography]>=3.3.0",
    "passlib[bcrypt]>=1.7.4",
    "python-multipart>=0.0.6",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.4",
    "pytest-asyncio>=0.23.3",
    "pytest-cov>=4.1.0",
    "httpx>=0.26.0",
    "black>=23.12.1",
    "ruff>=0.1.11",
    "mypy>=1.8.0",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
addopts = "--cov=src/study_helper --cov-report=html --cov-report=term-missing"

[tool.black]
line-length = 100
target-version = ['py314']

[tool.ruff]
line-length = 100
target-version = "py314"

[tool.mypy]
python_version = "3.14"
strict = true
```

---

## 2. Install Dependencies

```powershell
# Install production dependencies
uv add fastapi uvicorn sqlalchemy pydantic pydantic-settings alembic python-jose passlib python-multipart

# Install development dependencies
uv add --dev pytest pytest-asyncio pytest-cov httpx black ruff mypy
```

**Verify Installation:**
```powershell
uv run python -c "import fastapi; print(fastapi.__version__)"
```

---

## 3. Database Setup

### Create Database Configuration

Create `src/study_helper/core/config.py`:

```python
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./study_helper.db"
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
```

Create `.env` file (not committed to git):

```env
DATABASE_URL=sqlite:///./study_helper.db
SECRET_KEY=change-this-to-random-string-in-production
```

### Initialize Database Engine

Create `src/study_helper/db/base.py`:

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from src.study_helper.core.config import get_settings

settings = get_settings()

# Convert sqlite:/// to sqlite+aiosqlite:///
async_db_url = settings.DATABASE_URL.replace("sqlite://", "sqlite+aiosqlite://")

engine = create_async_engine(async_db_url, echo=True)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
```

### Configure Alembic

```powershell
# Initialize Alembic
uv run alembic init migrations
```

Edit `alembic.ini`:
```ini
# Replace this line
sqlalchemy.url = driver://user:pass@localhost/dbname

# With
sqlalchemy.url = sqlite:///./study_helper.db
```

Edit `migrations/env.py`:
```python
from src.study_helper.db.base import Base
from src.study_helper.models import *  # Import all models

target_metadata = Base.metadata
```

---

## 4. Create Initial Models

Create `src/study_helper/models/user.py` (minimal example):

```python
from sqlalchemy import String, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from src.study_helper.db.base import Base

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

Create `src/study_helper/models/__init__.py`:
```python
from .user import User
# Import other models as created

__all__ = ["User"]
```

### Generate and Apply Migration

```powershell
# Generate migration
uv run alembic revision --autogenerate -m "Initial schema"

# Apply migration
uv run alembic upgrade head
```

**Verify Database:**
```powershell
# SQLite command-line (if installed)
sqlite3 study_helper.db ".schema users"
```

---

## 5. Create Minimal FastAPI App

Create `src/study_helper/main.py`:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Study Helper API",
    description="Personal knowledge management for students",
    version="1.0.0"
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Study Helper API v1.0"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
```

---

## 6. Run Development Server

```powershell
# Start server with auto-reload
uv run uvicorn src.study_helper.main:app --reload --host 0.0.0.0 --port 8000
```

**Access Points:**
- API Root: http://localhost:8000
- Interactive Docs: http://localhost:8000/docs
- Alternative Docs: http://localhost:8000/redoc

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using StatReload
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

---

## 7. Run Tests

### Create First Test

Create `tests/contract/test_health.py`:

```python
from fastapi.testclient import TestClient
from src.study_helper.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
```

### Execute Tests

```powershell
# Run all tests with coverage
uv run pytest

# Run specific test file
uv run pytest tests/contract/test_health.py

# Run with verbose output
uv run pytest -v

# Generate HTML coverage report
uv run pytest --cov=src/study_helper --cov-report=html
# Open htmlcov/index.html in browser
```

**Expected Output:**
```
================================ test session starts =================================
collected 1 item

tests/contract/test_health.py .                                             [100%]

---------- coverage: platform win32, python 3.14.0-final-0 -----------
Name                              Stmts   Miss  Cover   Missing
---------------------------------------------------------------
src/study_helper/__init__.py          0      0   100%
src/study_helper/main.py             10      0   100%
---------------------------------------------------------------
TOTAL                                10      0   100%

================================= 1 passed in 0.25s ==================================
```

---

## 8. Code Quality Checks

### Format Code

```powershell
# Auto-format with Black
uv run black src tests

# Check without modifying
uv run black src tests --check
```

### Lint Code

```powershell
# Run Ruff linter
uv run ruff check src tests

# Auto-fix issues
uv run ruff check src tests --fix
```

### Type Checking

```powershell
# Run mypy for type validation
uv run mypy src
```

---

## 9. Frontend Setup (Optional)

### Create HTML Template

Create `templates/index.html`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Study Helper</title>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
</head>
<body class="bg-gray-100">
    <div id="app" class="container mx-auto p-4">
        <h1 class="text-3xl font-bold text-blue-600">Study Helper</h1>
        <p class="mt-2">Your personal knowledge management system</p>
    </div>
    <script src="/static/js/main.js"></script>
</body>
</html>
```

### Serve Static Files

Update `src/study_helper/main.py`:

```python
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pathlib import Path

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    index_path = Path("templates/index.html")
    return index_path.read_text()
```

---

## 10. Common Commands Reference

### Project Management

```powershell
# Add new dependency
uv add {package-name}

# Add dev dependency
uv add --dev {package-name}

# Update dependencies
uv lock --upgrade

# Show dependency tree
uv tree
```

### Database Migrations

```powershell
# Create new migration
uv run alembic revision --autogenerate -m "Description"

# Apply migrations
uv run alembic upgrade head

# Rollback one migration
uv run alembic downgrade -1

# Show current revision
uv run alembic current
```

### Testing

```powershell
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov

# Run specific test
uv run pytest tests/unit/test_models.py::test_user_creation

# Run tests matching pattern
uv run pytest -k "test_create"
```

### Development Server

```powershell
# Start with auto-reload
uv run uvicorn src.study_helper.main:app --reload

# Specify port
uv run uvicorn src.study_helper.main:app --reload --port 8080

# Production mode (no reload)
uv run uvicorn src.study_helper.main:app --host 0.0.0.0 --port 8000
```

---

## 11. Troubleshooting

### Issue: "Module not found" errors

**Solution:**
```powershell
# Ensure you're in the virtual environment
uv run python -c "import sys; print(sys.prefix)"

# Reinstall dependencies
uv sync
```

### Issue: Database locked (SQLite)

**Solution:**
```powershell
# Close all database connections
# Delete study_helper.db and recreate
Remove-Item study_helper.db
uv run alembic upgrade head
```

### Issue: Tests fail with "event loop closed"

**Solution:**
Ensure `pytest-asyncio` is installed and `pytest.ini` has:
```ini
[tool.pytest.ini_options]
asyncio_mode = "auto"
```

---

## 12. Next Steps

1. **Implement Models**: Create Course, Note, Task models per `data-model.md`
2. **Build Schemas**: Create Pydantic schemas for request/response validation
3. **Service Layer**: Implement business logic (auth, CRUD operations)
4. **API Routes**: Build FastAPI endpoints per `contracts/api-specification.md`
5. **Write Tests**: Follow TDD workflow (Red-Green-Refactor)
6. **Frontend**: Build vanilla JS components with Tailwind CSS

### Recommended Development Order

```
Phase 1: Authentication
├── models/user.py
├── schemas/auth.py
├── services/auth_service.py
├── api/auth.py
└── tests/contract/test_auth.py

Phase 2: Courses
├── models/course.py
├── schemas/course.py
├── services/course_service.py
├── api/courses.py
└── tests/integration/test_courses.py

Phase 3: Notes
├── models/note.py
├── schemas/note.py
├── services/note_service.py
├── api/notes.py
├── db/fts_setup.py (FTS5 triggers)
└── tests/unit/test_note_model.py

Phase 4: Tasks
├── models/task.py
├── schemas/task.py
├── services/task_service.py
├── api/tasks.py
└── tests/integration/test_task_subtasks.py

Phase 5: Search & Sync
├── services/search_service.py
├── services/sync_service.py
├── api/search.py
├── api/sync.py
└── tests/contract/test_search_performance.py
```

---

## Resources

- **FastAPI Documentation**: https://fastapi.tiangolo.com
- **SQLAlchemy 2.0 Tutorial**: https://docs.sqlalchemy.org/en/20/tutorial/
- **Pydantic V2 Docs**: https://docs.pydantic.dev/latest/
- **uv Documentation**: https://github.com/astral-sh/uv
- **Pytest Guide**: https://docs.pytest.org/en/stable/

---

**Happy Coding!** 🚀

For issues or questions, refer to:
- Feature Spec: `specs/001-student-knowledge-app/spec.md`
- Data Model: `specs/001-student-knowledge-app/data-model.md`
- API Contracts: `specs/001-student-knowledge-app/contracts/`
