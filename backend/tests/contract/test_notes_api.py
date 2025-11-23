"""Contract tests for Note API endpoints (T105-T108)."""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.study_helper.services.auth import register_user
from src.study_helper.services.course import create_course
from src.study_helper.services.note import create_note


@pytest.mark.asyncio
class TestNotesAPI:
    """Test Note API endpoints."""
    
    async def test_create_note_success(self, client: AsyncClient, db_session: AsyncSession):
        """T105 [RED]: Test POST /api/v1/notes creates a note and returns 201."""
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
        
        # Create note via API
        response = await client.post(
            "/api/v1/notes",
            json={
                "course_id": course.id,
                "title": "Lecture 1 Notes",
                "content": "# Introduction\n\nKey concepts...",
                "tags": "intro,basics"
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["course_id"] == course.id
        assert data["title"] == "Lecture 1 Notes"
        assert data["content"] == "# Introduction\n\nKey concepts..."
        assert data["tags"] == "intro,basics"
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data
        assert data["linked_tasks"] == []
    
    async def test_get_notes_by_course_filters_correctly(self, client: AsyncClient, db_session: AsyncSession):
        """T106 [RED]: Test GET /api/v1/courses/{course_id}/notes returns filtered notes."""
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
        
        # Create notes in different courses
        await create_note(
            db_session,
            course_id=course1.id,
            title="CS Note 1",
            content="Content 1"
        )
        await create_note(
            db_session,
            course_id=course1.id,
            title="CS Note 2",
            content="Content 2"
        )
        await create_note(
            db_session,
            course_id=course2.id,
            title="Math Note 1",
            content="Content 3"
        )
        
        # Login
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": "test@example.com", "password": "password123"}
        )
        token = login_response.json()["access_token"]
        
        # Get notes for course1
        response = await client.get(
            f"/api/v1/courses/{course1.id}/notes",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert all(note["course_id"] == course1.id for note in data)
        # Verify newest first (FR-016)
        assert data[0]["title"] == "CS Note 2"
        assert data[1]["title"] == "CS Note 1"
    
    async def test_update_note_returns_updated_data(self, client: AsyncClient, db_session: AsyncSession):
        """T107 [RED]: Test PATCH /api/v1/notes/{note_id} updates note."""
        # Register and login user
        user = await register_user(
            db_session,
            email="test@example.com",
            password="password123",
            full_name="Test User"
        )
        
        # Create course and note
        course = await create_course(
            db_session,
            user_id=user.id,
            name="CS 101",
            color="#3B82F6"
        )
        note = await create_note(
            db_session,
            course_id=course.id,
            title="Original Title",
            content="Original content"
        )
        
        # Login
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": "test@example.com", "password": "password123"}
        )
        token = login_response.json()["access_token"]
        
        # Update note
        response = await client.patch(
            f"/api/v1/notes/{note.id}",
            json={
                "title": "Updated Title",
                "content": "Updated content",
                "tags": "updated,new"
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == note.id
        assert data["title"] == "Updated Title"
        assert data["content"] == "Updated content"
        assert data["tags"] == "updated,new"
        assert data["updated_at"] != data["created_at"]
    
    async def test_delete_note_returns_204(self, client: AsyncClient, db_session: AsyncSession):
        """T108 [RED]: Test DELETE /api/v1/notes/{note_id} returns 204."""
        # Register and login user
        user = await register_user(
            db_session,
            email="test@example.com",
            password="password123",
            full_name="Test User"
        )
        
        # Create course and note
        course = await create_course(
            db_session,
            user_id=user.id,
            name="CS 101",
            color="#3B82F6"
        )
        note = await create_note(
            db_session,
            course_id=course.id,
            title="Test Note",
            content="Test content"
        )
        
        # Login
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": "test@example.com", "password": "password123"}
        )
        token = login_response.json()["access_token"]
        
        # Delete note
        response = await client.delete(
            f"/api/v1/notes/{note.id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 204
        
        # Verify note is deleted
        get_response = await client.get(
            f"/api/v1/courses/{course.id}/notes",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert len(get_response.json()) == 0
    
    async def test_create_note_requires_authentication(self, client: AsyncClient):
        """Test POST /api/v1/notes without authentication returns 401."""
        response = await client.post(
            "/api/v1/notes",
            json={
                "course_id": 1,
                "title": "Test",
                "content": "Content"
            }
        )
        
        assert response.status_code == 401
    
    async def test_get_notes_with_sort_parameters(self, client: AsyncClient, db_session: AsyncSession):
        """Test GET /api/v1/courses/{course_id}/notes with sort parameters."""
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
        
        # Create notes with different titles
        await create_note(
            db_session,
            course_id=course.id,
            title="Z Note",
            content="Content"
        )
        await create_note(
            db_session,
            course_id=course.id,
            title="A Note",
            content="Content"
        )
        
        # Login
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": "test@example.com", "password": "password123"}
        )
        token = login_response.json()["access_token"]
        
        # Get notes sorted by title ascending
        response = await client.get(
            f"/api/v1/courses/{course.id}/notes?sort_by=title&order=asc",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["title"] == "A Note"
        assert data[1]["title"] == "Z Note"
    
    async def test_link_note_to_task_success(self, client: AsyncClient, db_session: AsyncSession):
        """T203 [RED]: Test POST /api/v1/notes/{note_id}/link-task links note to task and returns 201."""
        from src.study_helper.services.task import create_task
        
        # Register user and create course
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
        
        # Create note and task
        note = await create_note(
            db_session,
            course_id=course.id,
            title="Lecture Notes",
            content="Content"
        )
        task = await create_task(
            db_session,
            course_id=course.id,
            title="Assignment",
            priority="high"
        )
        
        # Login
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": "test@example.com", "password": "password123"}
        )
        token = login_response.json()["access_token"]
        
        # Link note to task via API
        response = await client.post(
            f"/api/v1/notes/{note.id}/link-task",
            json={"task_id": task.id},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["note_id"] == note.id
        assert data["task_id"] == task.id
    
    async def test_link_note_to_task_duplicate_returns_409(self, client: AsyncClient, db_session: AsyncSession):
        """T204 [RED]: Test duplicate link returns 409 Conflict."""
        from src.study_helper.services.task import create_task
        from src.study_helper.services.note import link_note_to_task
        
        # Register user and create course
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
        
        # Create note and task
        note = await create_note(
            db_session,
            course_id=course.id,
            title="Notes",
            content="Content"
        )
        task = await create_task(
            db_session,
            course_id=course.id,
            title="Task",
            priority="medium"
        )
        
        # Create link directly
        await link_note_to_task(db_session, note.id, task.id)
        
        # Login
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": "test@example.com", "password": "password123"}
        )
        token = login_response.json()["access_token"]
        
        # Attempt duplicate link via API
        response = await client.post(
            f"/api/v1/notes/{note.id}/link-task",
            json={"task_id": task.id},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 409
        assert "already linked" in response.json()["detail"].lower()
    
    async def test_unlink_note_from_task_returns_204(self, client: AsyncClient, db_session: AsyncSession):
        """T205 [RED]: Test DELETE /api/v1/notes/{note_id}/link-task/{task_id} returns 204."""
        from src.study_helper.services.task import create_task
        from src.study_helper.services.note import link_note_to_task
        
        # Register user and create course
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
        
        # Create note and task
        note = await create_note(
            db_session,
            course_id=course.id,
            title="Notes",
            content="Content"
        )
        task = await create_task(
            db_session,
            course_id=course.id,
            title="Task",
            priority="low"
        )
        
        # Create link
        await link_note_to_task(db_session, note.id, task.id)
        
        # Login
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": "test@example.com", "password": "password123"}
        )
        token = login_response.json()["access_token"]
        
        # Unlink via API
        response = await client.delete(
            f"/api/v1/notes/{note.id}/link-task/{task.id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 204
