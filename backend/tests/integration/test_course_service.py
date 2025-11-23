"""Integration tests for Course service."""
import pytest
from sqlalchemy.exc import IntegrityError
from src.study_helper.models.user import User
from src.study_helper.models.course import Course
from src.study_helper.models.note import Note
from src.study_helper.models.task import Task
from src.study_helper.services.course import (
    create_course,
    get_courses,
    update_course,
    delete_course,
)


pytestmark = pytest.mark.asyncio


class TestCourseService:
    """Test course service functions with database (T064-T067)."""

    async def test_create_course(self, db_session):
        """T064 [RED]: Test creating a new course."""
        # Create user first
        user = User(
            email="course_test@example.com",
            hashed_password="hashed",
            full_name="Course Tester"
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        
        # Create course
        course = await create_course(
            db=db_session,
            user_id=user.id,
            name="Data Structures",
            description="Advanced algorithms",
            color="#FF5733"
        )
        
        assert course.id is not None
        assert course.user_id == user.id
        assert course.name == "Data Structures"
        assert course.description == "Advanced algorithms"
        assert course.color == "#FF5733"
        assert course.is_archived is False

    async def test_get_courses_filtered_by_archived_status(self, db_session):
        """T065 [RED]: Test filtering courses by is_archived status."""
        # Create user
        user = User(
            email="filter_test@example.com",
            hashed_password="hashed",
            full_name="Filter Tester"
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        
        # Create active courses
        active1 = await create_course(
            db=db_session,
            user_id=user.id,
            name="Active Course 1"
        )
        active2 = await create_course(
            db=db_session,
            user_id=user.id,
            name="Active Course 2"
        )
        
        # Create archived course
        archived = await create_course(
            db=db_session,
            user_id=user.id,
            name="Archived Course"
        )
        archived.is_archived = True
        await db_session.commit()
        
        # Get only active courses
        active_courses = await get_courses(
            db=db_session,
            user_id=user.id,
            is_archived=False
        )
        assert len(active_courses) == 2
        assert all(not c.is_archived for c in active_courses)
        
        # Get only archived courses
        archived_courses = await get_courses(
            db=db_session,
            user_id=user.id,
            is_archived=True
        )
        assert len(archived_courses) == 1
        assert archived_courses[0].is_archived is True
        
        # Get all courses (no filter)
        all_courses = await get_courses(
            db=db_session,
            user_id=user.id
        )
        assert len(all_courses) == 3

    async def test_update_course_archives_successfully(self, db_session):
        """T066 [RED]: Test updating course to archived status."""
        # Create user and course
        user = User(
            email="update_test@example.com",
            hashed_password="hashed",
            full_name="Update Tester"
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        
        course = await create_course(
            db=db_session,
            user_id=user.id,
            name="Course to Archive"
        )
        
        # Update to archive
        updated = await update_course(
            db=db_session,
            course_id=course.id,
            user_id=user.id,
            is_archived=True
        )
        
        assert updated.is_archived is True
        
        # Update name and color
        updated = await update_course(
            db=db_session,
            course_id=course.id,
            user_id=user.id,
            name="Updated Name",
            color="#00FF00"
        )
        
        assert updated.name == "Updated Name"
        assert updated.color == "#00FF00"

    async def test_delete_course_cascades_to_notes_and_tasks(self, db_session):
        """T067 [RED]: Test delete cascades to notes and tasks (critical business rule)."""
        # Create user
        user = User(
            email="delete_test@example.com",
            hashed_password="hashed",
            full_name="Delete Tester"
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        
        # Create course
        course = await create_course(
            db=db_session,
            user_id=user.id,
            name="Course to Delete"
        )
        
        # Create note and task in course
        note = Note(
            course_id=course.id,
            title="Note in course",
            content="This will be deleted"
        )
        task = Task(
            course_id=course.id,
            title="Task in course",
            priority="medium",
            status="pending"
        )
        db_session.add(note)
        db_session.add(task)
        await db_session.commit()
        
        note_id = note.id
        task_id = task.id
        
        # Delete course
        await delete_course(
            db=db_session,
            course_id=course.id,
            user_id=user.id
        )
        
        # Verify course was deleted
        from sqlalchemy import select
        result = await db_session.execute(
            select(Course).where(Course.id == course.id)
        )
        deleted_course = result.scalar_one_or_none()
        assert deleted_course is None
        
        # Verify note was cascade deleted
        result = await db_session.execute(
            select(Note).where(Note.id == note_id)
        )
        deleted_note = result.scalar_one_or_none()
        assert deleted_note is None
        
        # Verify task was cascade deleted
        result = await db_session.execute(
            select(Task).where(Task.id == task_id)
        )
        deleted_task = result.scalar_one_or_none()
        assert deleted_task is None
