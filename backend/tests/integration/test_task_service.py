"""Integration tests for Task service layer (T129-T132)."""
import pytest
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from src.study_helper.services.auth import register_user
from src.study_helper.services.course import create_course
from src.study_helper.services.task import (
    create_task,
    get_tasks_by_course,
    update_task,
    delete_task,
)
from src.study_helper.models.task import Task


@pytest.mark.asyncio
class TestTaskService:
    """Test Task service layer."""
    
    async def test_create_task(self, db_session: AsyncSession):
        """T129 [RED]: Test creating a task."""
        # Create user and course
        user = await register_user(
            db_session,
            email="test@example.com",
            password="password123",
            full_name="Test User"
        )
        course = await create_course(
            db_session,
            user_id=user.id,
            name="CS 101",
            color="#3B82F6"
        )
        
        # Create task
        due_date = datetime.utcnow() + timedelta(days=7)
        task = await create_task(
            db=db_session,
            course_id=course.id,
            title="Complete Assignment 1",
            description="Finish coding exercises",
            due_date=due_date,
            priority="high"
        )
        
        assert task.id is not None
        assert task.course_id == course.id
        assert task.title == "Complete Assignment 1"
        assert task.description == "Finish coding exercises"
        assert task.priority == "high"
        assert task.status == "pending"
        assert task.completed_at is None
    
    async def test_get_tasks_by_course_sorted_oldest_first(self, db_session: AsyncSession):
        """T130 [RED]: Test getting tasks sorted by created_at asc (FR-029 default)."""
        # Create user and course
        user = await register_user(
            db_session,
            email="test@example.com",
            password="password123",
            full_name="Test User"
        )
        course = await create_course(
            db_session,
            user_id=user.id,
            name="CS 101",
            color="#3B82F6"
        )
        
        # Create multiple tasks
        task1 = await create_task(
            db_session,
            course_id=course.id,
            title="Task 1"
        )
        task2 = await create_task(
            db_session,
            course_id=course.id,
            title="Task 2"
        )
        task3 = await create_task(
            db_session,
            course_id=course.id,
            title="Task 3"
        )
        
        # Get tasks (default sort: oldest first)
        tasks = await get_tasks_by_course(
            db=db_session,
            course_id=course.id
        )
        
        assert len(tasks) == 3
        # Oldest first (task1, task2, task3)
        assert tasks[0].title == "Task 1"
        assert tasks[1].title == "Task 2"
        assert tasks[2].title == "Task 3"
    
    async def test_mark_task_complete_sets_completed_at(self, db_session: AsyncSession):
        """T131 [RED]: Test marking task as complete sets completed_at timestamp."""
        # Create user, course, and task
        user = await register_user(
            db_session,
            email="test@example.com",
            password="password123",
            full_name="Test User"
        )
        course = await create_course(
            db_session,
            user_id=user.id,
            name="CS 101",
            color="#3B82F6"
        )
        task = await create_task(
            db_session,
            course_id=course.id,
            title="Test Task"
        )
        
        assert task.status == "pending"
        assert task.completed_at is None
        
        # Mark as complete
        updated_task = await update_task(
            db=db_session,
            task_id=task.id,
            is_completed=True
        )
        
        assert updated_task.status == "completed"
        assert updated_task.completed_at is not None
        assert isinstance(updated_task.completed_at, datetime)
    
    async def test_delete_task_succeeds(self, db_session: AsyncSession):
        """T132 [RED]: Test deleting a task."""
        # Create user, course, and task
        user = await register_user(
            db_session,
            email="test@example.com",
            password="password123",
            full_name="Test User"
        )
        course = await create_course(
            db_session,
            user_id=user.id,
            name="CS 101",
            color="#3B82F6"
        )
        task = await create_task(
            db_session,
            course_id=course.id,
            title="Test Task"
        )
        
        # Delete task
        await delete_task(
            db=db_session,
            task_id=task.id
        )
        
        # Verify task is deleted
        from sqlalchemy.future import select
        result = await db_session.execute(
            select(Task).where(Task.id == task.id)
        )
        deleted_task = result.scalar_one_or_none()
        
        assert deleted_task is None

    async def test_get_tasks_today_view(self, db_session: AsyncSession):
        """T167 [RED]: Test getting tasks due today."""
        # Create user and course
        user = await register_user(
            db_session,
            email="today@example.com",
            password="password123",
            full_name="Test User"
        )
        course = await create_course(
            db_session,
            user_id=user.id,
            name="CS 101",
            color="#3B82F6"
        )
        
        # Create tasks with different due dates
        today = datetime.utcnow().date()
        await create_task(db_session, course.id, "Today Task", due_date=today)
        await create_task(db_session, course.id, "Tomorrow Task", due_date=today + timedelta(days=1))
        await create_task(db_session, course.id, "Next Week Task", due_date=today + timedelta(days=10))
        
        # Get today's tasks
        tasks = await get_tasks_by_course(
            db=db_session,
            course_id=course.id,
            view="today"
        )
        
        assert len(tasks) == 1
        assert tasks[0].title == "Today Task"

    async def test_get_tasks_this_week_view_includes_today(self, db_session: AsyncSession):
        """T168 [RED]: Test getting tasks due this week (includes today)."""
        # Create user and course
        user = await register_user(
            db_session,
            email="week@example.com",
            password="password123",
            full_name="Test User"
        )
        course = await create_course(
            db_session,
            user_id=user.id,
            name="CS 101",
            color="#3B82F6"
        )
        
        # Create tasks
        today = datetime.utcnow().date()
        await create_task(db_session, course.id, "Today", due_date=today)
        await create_task(db_session, course.id, "In 3 Days", due_date=today + timedelta(days=3))
        await create_task(db_session, course.id, "In 7 Days", due_date=today + timedelta(days=7))
        await create_task(db_session, course.id, "In 10 Days", due_date=today + timedelta(days=10))
        
        # Get this week's tasks
        tasks = await get_tasks_by_course(
            db=db_session,
            course_id=course.id,
            view="week"
        )
        
        assert len(tasks) == 3  # Today, +3 days, +7 days
        titles = {task.title for task in tasks}
        assert "Today" in titles
        assert "In 3 Days" in titles
        assert "In 7 Days" in titles
        assert "In 10 Days" not in titles

    async def test_get_tasks_upcoming_view(self, db_session: AsyncSession):
        """T169 [RED]: Test getting upcoming tasks (beyond this week)."""
        # Create user and course
        user = await register_user(
            db_session,
            email="upcoming@example.com",
            password="password123",
            full_name="Test User"
        )
        course = await create_course(
            db_session,
            user_id=user.id,
            name="CS 101",
            color="#3B82F6"
        )
        
        # Create tasks
        today = datetime.utcnow().date()
        await create_task(db_session, course.id, "Today", due_date=today)
        await create_task(db_session, course.id, "This Week", due_date=today + timedelta(days=5))
        await create_task(db_session, course.id, "Upcoming 1", due_date=today + timedelta(days=10))
        await create_task(db_session, course.id, "Upcoming 2", due_date=today + timedelta(days=20))
        
        # Get upcoming tasks
        tasks = await get_tasks_by_course(
            db=db_session,
            course_id=course.id,
            view="upcoming"
        )
        
        assert len(tasks) == 2
        titles = {task.title for task in tasks}
        assert "Upcoming 1" in titles
        assert "Upcoming 2" in titles

    async def test_tasks_without_due_date_appear_in_no_due_date_section(self, db_session: AsyncSession):
        """T170 [RED]: Test tasks without due dates are handled separately."""
        # Create user and course
        user = await register_user(
            db_session,
            email="nodue@example.com",
            password="password123",
            full_name="Test User"
        )
        course = await create_course(
            db_session,
            user_id=user.id,
            name="CS 101",
            color="#3B82F6"
        )
        
        # Create tasks
        today = datetime.utcnow().date()
        await create_task(db_session, course.id, "No Due Date")  # No due_date
        await create_task(db_session, course.id, "Has Due Date", due_date=today)
        
        # Get all tasks
        all_tasks = await get_tasks_by_course(db_session, course.id)
        assert len(all_tasks) == 2
        
        # Get today's tasks (should not include no-due-date task)
        today_tasks = await get_tasks_by_course(db_session, course.id, view="today")
        assert len(today_tasks) == 1
        assert today_tasks[0].title == "Has Due Date"

