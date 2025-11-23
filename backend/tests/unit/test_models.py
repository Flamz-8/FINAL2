"""Unit tests for SQLAlchemy models."""
import pytest
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError


pytestmark = pytest.mark.asyncio


class TestUserModel:
    """Test suite for User model (T017, T018)."""
    
    async def test_user_creation(self, db_session):
        """T017 [RED]: Verify User model with email uniqueness."""
        from src.study_helper.models.user import User
        
        # Create user
        user = User(
            email="test@example.com",
            hashed_password="hashed_password_here",
            full_name="Test User"
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        
        # Verify user was created
        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.full_name == "Test User"
        assert user.hashed_password == "hashed_password_here"
        assert isinstance(user.created_at, datetime)
        
        # Test email uniqueness constraint
        duplicate_user = User(
            email="test@example.com",  # Same email
            hashed_password="different_password",
            full_name="Another User"
        )
        db_session.add(duplicate_user)
        
        with pytest.raises(IntegrityError):
            await db_session.commit()
    
    async def test_user_email_index(self, db_session):
        """T018 [RED]: Verify email index exists for login performance."""
        from src.study_helper.models.user import User
        from sqlalchemy import inspect
        
        # Get inspector synchronously via run_sync
        async def get_indexes():
            async with db_session.bind.connect() as conn:
                def _get_indexes(sync_conn):
                    inspector = inspect(sync_conn)
                    return inspector.get_indexes('users')
                return await conn.run_sync(_get_indexes)
        
        indexes = await get_indexes()
        
        # Verify email index exists
        email_indexes = [idx for idx in indexes if 'email' in idx['column_names']]
        assert len(email_indexes) > 0, "Email index not found for login performance"


class TestCourseModel:
    """Test suite for Course model (T051, T052)."""
    
    async def test_course_creation(self, db_session):
        """T051 [RED]: Verify Course model creation with relationships."""
        from src.study_helper.models.user import User
        from src.study_helper.models.course import Course
        
        # Create user first
        user = User(
            email="student@example.com",
            hashed_password="hashed_password",
            full_name="Student User"
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        
        # Create course
        course = Course(
            user_id=user.id,
            name="CS 101 - Intro to Programming",
            description="Learn Python fundamentals",
            color="#3B82F6",
            is_archived=False
        )
        db_session.add(course)
        await db_session.commit()
        await db_session.refresh(course)
        
        # Verify course was created
        assert course.id is not None
        assert course.user_id == user.id
        assert course.name == "CS 101 - Intro to Programming"
        assert course.description == "Learn Python fundamentals"
        assert course.color == "#3B82F6"
        assert course.is_archived is False
        assert isinstance(course.created_at, datetime)
        assert isinstance(course.updated_at, datetime)
    
    async def test_course_cascade_delete(self, db_session):
        """T052 [RED]: Verify cascade delete removes notes and tasks (Clarification #1)."""
        from src.study_helper.models.user import User
        from src.study_helper.models.course import Course
        from src.study_helper.models.note import Note
        from src.study_helper.models.task import Task
        
        # Create user
        user = User(
            email="cascade@example.com",
            hashed_password="hashed_password",
            full_name="Cascade User"
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        
        # Create course
        course = Course(
            user_id=user.id,
            name="CS 202",
            color="#3B82F6"
        )
        db_session.add(course)
        await db_session.commit()
        await db_session.refresh(course)
        
        # Create note in course
        note = Note(
            course_id=course.id,
            title="Lecture 1 Notes",
            content="Introduction to data structures"
        )
        db_session.add(note)
        
        # Create task in course
        task = Task(
            course_id=course.id,
            title="Assignment 1",
            description="Complete problem set",
            priority="medium",
            status="pending"
        )
        db_session.add(task)
        await db_session.commit()
        
        note_id = note.id
        task_id = task.id
        
        # Delete course (should cascade delete note and task)
        await db_session.delete(course)
        await db_session.commit()
        
        # Verify note was deleted
        result = await db_session.execute(
            select(Note).where(Note.id == note_id)
        )
        deleted_note = result.scalar_one_or_none()
        assert deleted_note is None, "Note should be deleted when course is deleted"
        
        # Verify task was deleted
        result = await db_session.execute(
            select(Task).where(Task.id == task_id)
        )
        deleted_task = result.scalar_one_or_none()
        assert deleted_task is None, "Task should be deleted when course is deleted"


class TestNoteTaskLink:
    """Test suite for NoteTaskLink model (T188-T189)."""
    
    async def test_note_task_link_creation(self, db_session):
        """T188 [RED]: Verify NoteTaskLink model creates links between notes and tasks."""
        from src.study_helper.models.user import User
        from src.study_helper.models.course import Course
        from src.study_helper.models.note import Note
        from src.study_helper.models.task import Task
        from src.study_helper.models.note_task_link import NoteTaskLink
        
        # Create user and course
        user = User(email="test@example.com", hashed_password="pwd", full_name="Test User")
        db_session.add(user)
        await db_session.commit()
        
        course = Course(user_id=user.id, title="CS 101", color="#3B82F6")
        db_session.add(course)
        await db_session.commit()
        
        # Create note and task
        note = Note(course_id=course.id, title="Lecture 1", content="Notes content")
        task = Task(course_id=course.id, title="Assignment 1", priority="high")
        db_session.add_all([note, task])
        await db_session.commit()
        
        # Create link
        link = NoteTaskLink(note_id=note.id, task_id=task.id)
        db_session.add(link)
        await db_session.commit()
        
        # Verify link was created
        result = await db_session.execute(
            select(NoteTaskLink).where(
                NoteTaskLink.note_id == note.id,
                NoteTaskLink.task_id == task.id
            )
        )
        created_link = result.scalar_one_or_none()
        assert created_link is not None
        assert created_link.note_id == note.id
        assert created_link.task_id == task.id
    
    async def test_note_task_link_unique_constraint(self, db_session):
        """T189 [RED]: Verify unique constraint prevents duplicate links."""
        from src.study_helper.models.user import User
        from src.study_helper.models.course import Course
        from src.study_helper.models.note import Note
        from src.study_helper.models.task import Task
        from src.study_helper.models.note_task_link import NoteTaskLink
        
        # Create user, course, note, and task
        user = User(email="test@example.com", hashed_password="pwd", full_name="Test User")
        db_session.add(user)
        await db_session.commit()
        
        course = Course(user_id=user.id, title="CS 101", color="#3B82F6")
        db_session.add(course)
        await db_session.commit()
        
        note = Note(course_id=course.id, title="Lecture 1", content="Notes")
        task = Task(course_id=course.id, title="Assignment 1", priority="medium")
        db_session.add_all([note, task])
        await db_session.commit()
        
        # Create first link
        link1 = NoteTaskLink(note_id=note.id, task_id=task.id)
        db_session.add(link1)
        await db_session.commit()
        
        # Attempt to create duplicate link
        link2 = NoteTaskLink(note_id=note.id, task_id=task.id)
        db_session.add(link2)
        
        with pytest.raises(IntegrityError):
            await db_session.commit()

