"""Unit tests for Pydantic schemas validation."""
import pytest
from pydantic import ValidationError
from src.study_helper.schemas.user import (
    UserRegister,
    UserResponse,
    UserLogin,
    TokenResponse,
)
from datetime import datetime


class TestUserRegisterSchema:
    """Test UserRegister schema validation."""

    def test_user_register_validation(self):
        """Test valid user registration data."""
        data = {
            "email": "test@example.com",
            "password": "securepass123",
            "full_name": "John Doe"
        }
        user = UserRegister(**data)
        
        assert user.email == "test@example.com"
        assert user.password == "securepass123"
        assert user.full_name == "John Doe"

    def test_user_register_invalid_email(self):
        """Test registration with invalid email format."""
        data = {
            "email": "not-an-email",
            "password": "securepass123",
            "full_name": "John Doe"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            UserRegister(**data)
        
        errors = exc_info.value.errors()
        assert any(err['loc'] == ('email',) for err in errors)

    def test_user_register_password_too_short(self):
        """Test registration with password < 8 characters."""
        data = {
            "email": "test@example.com",
            "password": "short",  # Only 5 chars
            "full_name": "John Doe"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            UserRegister(**data)
        
        errors = exc_info.value.errors()
        assert any(err['loc'] == ('password',) for err in errors)


class TestUserResponseSchema:
    """Test UserResponse schema (no password field)."""

    def test_user_response_structure(self):
        """Test UserResponse excludes password."""
        data = {
            "id": 1,
            "email": "test@example.com",
            "full_name": "John Doe",
            "created_at": datetime.utcnow()
        }
        user_response = UserResponse(**data)
        
        assert user_response.id == 1
        assert user_response.email == "test@example.com"
        assert user_response.full_name == "John Doe"
        assert isinstance(user_response.created_at, datetime)
        
        # Verify password is NOT in schema
        assert not hasattr(user_response, 'password')
        assert not hasattr(user_response, 'hashed_password')


class TestUserLoginSchema:
    """Test UserLogin schema."""

    def test_user_login_validation(self):
        """Test valid login credentials."""
        data = {
            "email": "test@example.com",
            "password": "mypassword"
        }
        login = UserLogin(**data)
        
        assert login.email == "test@example.com"
        assert login.password == "mypassword"


class TestTokenResponseSchema:
    """Test TokenResponse schema with user data."""

    def test_token_response_structure(self):
        """Test TokenResponse includes access_token and user."""
        user_data = {
            "id": 1,
            "email": "test@example.com",
            "full_name": "John Doe",
            "created_at": datetime.utcnow()
        }
        
        token_data = {
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "token_type": "bearer",
            "user": user_data
        }
        
        token_response = TokenResponse(**token_data)
        
        assert token_response.access_token == "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        assert token_response.token_type == "bearer"
        assert token_response.user.id == 1
        assert token_response.user.email == "test@example.com"


class TestCourseSchemas:
    """Test Course schema validation (T057, T058)."""

    def test_course_create_valid_color(self):
        """T057 [RED]: Test CourseCreate with valid hex color."""
        from src.study_helper.schemas.course import CourseCreate
        
        data = {
            "name": "CS 101",
            "description": "Introduction to Programming",
            "color": "#FF5733"
        }
        course = CourseCreate(**data)
        
        assert course.name == "CS 101"
        assert course.description == "Introduction to Programming"
        assert course.color == "#FF5733"

    def test_course_create_invalid_color_fails(self):
        """T058 [RED]: Test CourseCreate with invalid color format."""
        from src.study_helper.schemas.course import CourseCreate
        
        # Invalid color format (no #)
        with pytest.raises(ValidationError) as exc_info:
            CourseCreate(name="CS 101", color="FF5733")
        
        errors = exc_info.value.errors()
        assert any(err['loc'] == ('color',) for err in errors)
        
        # Invalid color (wrong length)
        with pytest.raises(ValidationError):
            CourseCreate(name="CS 101", color="#FFF")
        
        # Invalid color (non-hex characters)
        with pytest.raises(ValidationError):
            CourseCreate(name="CS 101", color="#GGGGGG")

    def test_course_create_name_max_length(self):
        """T063 [REFACTOR]: Test name max 200 chars validation."""
        from src.study_helper.schemas.course import CourseCreate
        
        # Valid: exactly 200 chars
        long_name = "A" * 200
        course = CourseCreate(name=long_name)
        assert course.name == long_name
        
        # Invalid: 201 chars
        with pytest.raises(ValidationError) as exc_info:
            CourseCreate(name="A" * 201)
        
        errors = exc_info.value.errors()
        assert any(err['loc'] == ('name',) for err in errors)

    def test_course_create_description_max_length(self):
        """T063 [REFACTOR]: Test description max 2000 chars validation."""
        from src.study_helper.schemas.course import CourseCreate
        
        # Valid: exactly 2000 chars
        long_desc = "A" * 2000
        course = CourseCreate(name="CS 101", description=long_desc)
        assert course.description == long_desc
        
        # Invalid: 2001 chars
        with pytest.raises(ValidationError) as exc_info:
            CourseCreate(name="CS 101", description="A" * 2001)
        
        errors = exc_info.value.errors()
        assert any(err['loc'] == ('description',) for err in errors)

    def test_course_update_all_optional(self):
        """T061 [GREEN]: Test CourseUpdate with all optional fields."""
        from src.study_helper.schemas.course import CourseUpdate
        
        # All fields optional - empty update is valid
        update = CourseUpdate()
        assert update.model_dump(exclude_unset=True) == {}
        
        # Partial update
        update = CourseUpdate(name="New Name")
        assert update.name == "New Name"
        assert update.description is None
        
        # Archive course
        update = CourseUpdate(is_archived=True)
        assert update.is_archived is True

    def test_course_response_with_counts(self):
        """T062 [GREEN]: Test CourseResponse includes notes_count and tasks_count."""
        from src.study_helper.schemas.course import CourseResponse
        
        data = {
            "id": 1,
            "user_id": 1,
            "name": "CS 101",
            "description": "Intro to Programming",
            "color": "#3B82F6",
            "is_archived": False,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "notes_count": 5,
            "tasks_count": 3
        }
        
        course_response = CourseResponse(**data)
        
        assert course_response.id == 1
        assert course_response.name == "CS 101"
        assert course_response.notes_count == 5
        assert course_response.tasks_count == 3


class TestNoteSchemas:
    """Test Note schemas (T089-T091)."""
    
    def test_note_create_validation(self):
        """T089 [RED]: Test NoteCreate requires title and content."""
        from src.study_helper.schemas.note import NoteCreate
        
        data = {
            "course_id": 1,
            "title": "Lecture 1 Notes",
            "content": "# Introduction\n\nKey concepts..."
        }
        note = NoteCreate(**data)
        
        assert note.course_id == 1
        assert note.title == "Lecture 1 Notes"
        assert note.content == "# Introduction\n\nKey concepts..."
        assert note.tags is None  # Optional field
    
    def test_note_title_max_length_300(self):
        """T090 [RED]: Test title max length is 300 chars."""
        from src.study_helper.schemas.note import NoteCreate
        from pydantic import ValidationError
        import pytest
        
        long_title = "A" * 301
        
        with pytest.raises(ValidationError) as exc_info:
            NoteCreate(
                course_id=1,
                title=long_title,
                content="Some content"
            )
        
        errors = exc_info.value.errors()
        assert any("title" in str(error) for error in errors)
    
    def test_note_content_max_length_50000(self):
        """T091 [RED]: Test content max length is 50,000 chars."""
        from src.study_helper.schemas.note import NoteCreate
        from pydantic import ValidationError
        import pytest
        
        long_content = "A" * 50001
        
        with pytest.raises(ValidationError) as exc_info:
            NoteCreate(
                course_id=1,
                title="Test Note",
                content=long_content
            )
        
        errors = exc_info.value.errors()
        assert any("content" in str(error) for error in errors)


class TestTaskSchemas:
    """Test Task schemas (T123-T124)."""
    
    def test_task_create_with_empty_title_generates_placeholder(self):
        """T123 [RED]: Test TaskCreate with empty title generates placeholder."""
        from src.study_helper.schemas.task import TaskCreate
        
        # Test with empty string - should generate placeholder
        data = {
            "course_id": 1,
            "title": "",
            "description": "Task description"
        }
        task = TaskCreate(**data)
        
        assert task.title.startswith("Untitled Task")
        assert task.course_id == 1
    
    def test_task_priority_validation(self):
        """T124 [RED]: Test task priority only allows low/medium/high."""
        from src.study_helper.schemas.task import TaskCreate
        from pydantic import ValidationError
        import pytest
        
        # Valid priorities
        for priority in ["low", "medium", "high"]:
            task = TaskCreate(
                course_id=1,
                title="Test Task",
                priority=priority
            )
            assert task.priority == priority
        
        # Invalid priority
        with pytest.raises(ValidationError) as exc_info:
            TaskCreate(
                course_id=1,
                title="Test Task",
                priority="urgent"  # Invalid
            )
        
        errors = exc_info.value.errors()
        assert any("priority" in str(error) for error in errors)
