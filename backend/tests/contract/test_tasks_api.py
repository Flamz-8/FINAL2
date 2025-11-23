"""Contract tests for Task API endpoints (T138-T141)."""
import pytest
from datetime import datetime, timedelta
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.study_helper.services.auth import register_user
from src.study_helper.services.course import create_course
from src.study_helper.services.task import create_task


@pytest.mark.asyncio
class TestTasksAPI:
    """Test Task API endpoints."""
    
    async def test_create_task_success(self, client: AsyncClient, db_session: AsyncSession):
        """T138 [RED]: Test POST /api/v1/tasks creates a task and returns 201."""
        # Register and login user
        user = await register_user(
            db_session,
            email="test@example.com",
            password="password123",
            full_name="Test User"
        )
        
        # Create course
        course = await create_course(
            db_session,
            user_id=user.id,
            name="CS 101",
            color="#3B82F6"
        )
        
        # Login to get token
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": "test@example.com", "password": "password123"}
        )
        token = login_response.json()["access_token"]
        
        # Create task via API
        due_date = (datetime.utcnow() + timedelta(days=7)).isoformat()
        response = await client.post(
            "/api/v1/tasks",
            json={
                "course_id": course.id,
                "title": "Complete Assignment 1",
                "description": "Finish coding exercises",
                "due_date": due_date,
                "priority": "high"
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["course_id"] == course.id
        assert data["title"] == "Complete Assignment 1"
        assert data["description"] == "Finish coding exercises"
        assert data["priority"] == "high"
        assert data["status"] == "pending"
        assert data["completed_at"] is None
        assert "id" in data
        assert "created_at" in data
        assert data["subtasks"] == []
        assert data["linked_notes_count"] == 0
    
    async def test_get_tasks_by_course_returns_correct_tasks(self, client: AsyncClient, db_session: AsyncSession):
        """T139 [RED]: Test GET /api/v1/courses/{course_id}/tasks returns filtered tasks."""
        # Register and login user
        user = await register_user(
            db_session,
            email="test@example.com",
            password="password123",
            full_name="Test User"
        )
        
        # Create courses
        course1 = await create_course(
            db_session,
            user_id=user.id,
            name="CS 101",
            color="#3B82F6"
        )
        course2 = await create_course(
            db_session,
            user_id=user.id,
            name="Math 201",
            color="#EF4444"
        )
        
        # Create tasks in different courses
        await create_task(
            db_session,
            course_id=course1.id,
            title="CS Task 1"
        )
        await create_task(
            db_session,
            course_id=course1.id,
            title="CS Task 2"
        )
        await create_task(
            db_session,
            course_id=course2.id,
            title="Math Task 1"
        )
        
        # Login
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": "test@example.com", "password": "password123"}
        )
        token = login_response.json()["access_token"]
        
        # Get tasks for course1
        response = await client.get(
            f"/api/v1/courses/{course1.id}/tasks",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert all(task["course_id"] == course1.id for task in data)
        # Verify oldest first (FR-029)
        assert data[0]["title"] == "CS Task 1"
        assert data[1]["title"] == "CS Task 2"
    
    async def test_mark_task_complete_via_patch(self, client: AsyncClient, db_session: AsyncSession):
        """T140 [RED]: Test PATCH /api/v1/tasks/{task_id} marks task as complete."""
        # Register and login user
        user = await register_user(
            db_session,
            email="test@example.com",
            password="password123",
            full_name="Test User"
        )
        
        # Create course and task
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
        
        # Login
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": "test@example.com", "password": "password123"}
        )
        token = login_response.json()["access_token"]
        
        # Mark task as complete
        response = await client.patch(
            f"/api/v1/tasks/{task.id}",
            json={"is_completed": True},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == task.id
        assert data["status"] == "completed"
        assert data["completed_at"] is not None
    
    async def test_delete_task_returns_204(self, client: AsyncClient, db_session: AsyncSession):
        """T141 [RED]: Test DELETE /api/v1/tasks/{task_id} returns 204."""
        # Register and login user
        user = await register_user(
            db_session,
            email="test@example.com",
            password="password123",
            full_name="Test User"
        )
        
        # Create course and task
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
        
        # Login
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": "test@example.com", "password": "password123"}
        )
        token = login_response.json()["access_token"]
        
        # Delete task
        response = await client.delete(
            f"/api/v1/tasks/{task.id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 204
        
        # Verify task is deleted
        get_response = await client.get(
            f"/api/v1/courses/{course.id}/tasks",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert len(get_response.json()) == 0
    
    async def test_create_task_requires_authentication(self, client: AsyncClient):
        """Test POST /api/v1/tasks without authentication returns 401."""
        response = await client.post(
            "/api/v1/tasks",
            json={
                "course_id": 1,
                "title": "Test Task"
            }
        )
        
        assert response.status_code == 401
    
    async def test_get_tasks_with_completed_filter(self, client: AsyncClient, db_session: AsyncSession):
        """Test GET /api/v1/courses/{course_id}/tasks with completed filter."""
        # Register and login user
        user = await register_user(
            db_session,
            email="test@example.com",
            password="password123",
            full_name="Test User"
        )
        
        # Create course
        course = await create_course(
            db_session,
            user_id=user.id,
            name="CS 101",
            color="#3B82F6"
        )
        
        # Create pending and completed tasks
        from src.study_helper.services.task import update_task
        
        task1 = await create_task(
            db_session,
            course_id=course.id,
            title="Pending Task"
        )
        task2 = await create_task(
            db_session,
            course_id=course.id,
            title="Completed Task"
        )
        await update_task(db_session, task2.id, is_completed=True)
        
        # Login
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": "test@example.com", "password": "password123"}
        )
        token = login_response.json()["access_token"]
        
        # Get only pending tasks
        response = await client.get(
            f"/api/v1/courses/{course.id}/tasks?completed=false",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "Pending Task"
        assert data[0]["status"] == "pending"

    async def test_get_tasks_today_view_returns_only_today(self, client: AsyncClient, db_session: AsyncSession):
        """T175 [RED]: Test GET /api/v1/courses/{id}/tasks?view=today returns only today's tasks."""
        from datetime import datetime, timedelta
        
        # Register and login
        user = await register_user(db_session, "test@example.com", "password123", "Test User")
        course = await create_course(db_session, user.id, "CS 101", "#3B82F6")
        
        # Create tasks with different due dates
        today = datetime.utcnow().date()
        await create_task(db_session, course.id, "Today Task", due_date=today)
        await create_task(db_session, course.id, "Tomorrow Task", due_date=today + timedelta(days=1))
        await create_task(db_session, course.id, "Next Week", due_date=today + timedelta(days=10))
        
        # Login
        login_response = await client.post("/api/v1/auth/login", json={"email": "test@example.com", "password": "password123"})
        token = login_response.json()["access_token"]
        
        # Get today's tasks
        response = await client.get(
            f"/api/v1/courses/{course.id}/tasks?view=today",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "Today Task"

    async def test_get_tasks_week_view_aggregates_across_courses(self, client: AsyncClient, db_session: AsyncSession):
        """T176 [RED]: Test GET /api/v1/tasks/week returns this week's tasks from all courses."""
        from datetime import datetime, timedelta
        
        # Register and login
        user = await register_user(db_session, "test@example.com", "password123", "Test User")
        course1 = await create_course(db_session, user.id, "CS 101", "#3B82F6")
        course2 = await create_course(db_session, user.id, "Math 201", "#10B981")
        
        # Create tasks in different courses
        today = datetime.utcnow().date()
        await create_task(db_session, course1.id, "CS Task Today", due_date=today)
        await create_task(db_session, course2.id, "Math Task This Week", due_date=today + timedelta(days=3))
        await create_task(db_session, course1.id, "CS Task Next Month", due_date=today + timedelta(days=30))
        
        # Login
        login_response = await client.post("/api/v1/auth/login", json={"email": "test@example.com", "password": "password123"})
        token = login_response.json()["access_token"]
        
        # Get this week's tasks across all courses
        response = await client.get(
            "/api/v1/tasks/week",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        titles = {task["title"] for task in data}
        assert "CS Task Today" in titles
        assert "Math Task This Week" in titles

    async def test_get_tasks_upcoming_view_sorted_by_date(self, client: AsyncClient, db_session: AsyncSession):
        """T177 [RED]: Test GET /api/v1/tasks/upcoming returns future tasks sorted by due_date."""
        from datetime import datetime, timedelta
        
        # Register and login
        user = await register_user(db_session, "test@example.com", "password123", "Test User")
        course = await create_course(db_session, user.id, "CS 101", "#3B82F6")
        
        # Create upcoming tasks
        today = datetime.utcnow().date()
        await create_task(db_session, course.id, "Far Future", due_date=today + timedelta(days=30))
        await create_task(db_session, course.id, "Near Future", due_date=today + timedelta(days=10))
        await create_task(db_session, course.id, "This Week", due_date=today + timedelta(days=3))
        
        # Login
        login_response = await client.post("/api/v1/auth/login", json={"email": "test@example.com", "password": "password123"})
        token = login_response.json()["access_token"]
        
        # Get upcoming tasks
        response = await client.get(
            "/api/v1/tasks/upcoming",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2  # Only tasks beyond this week
        assert data[0]["title"] == "Near Future"  # Sorted by due_date ascending
        assert data[1]["title"] == "Far Future"

