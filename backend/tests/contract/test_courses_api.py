"""Contract tests for Course API endpoints."""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from src.study_helper.models.user import User
from src.study_helper.services.auth import register_user
from src.study_helper.services.course import create_course


pytestmark = pytest.mark.asyncio


class TestCoursesAPI:
    """Test Course API contract per api-specification.md (T073-T076)."""

    async def test_create_course_success(self, client: AsyncClient, db_session: AsyncSession):
        """T073 [RED]: Test POST /api/v1/courses with authentication."""
        # Register and login user
        user = await register_user(
            db=db_session,
            email="course_api@example.com",
            password="password123",
            full_name="Course API User"
        )
        
        # Login to get token
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": "course_api@example.com", "password": "password123"}
        )
        token = login_response.json()["access_token"]
        
        # Create course
        response = await client.post(
            "/api/v1/courses",
            json={
                "name": "CS 101",
                "description": "Introduction to Programming",
                "color": "#3B82F6"
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 201
        data = response.json()
        
        assert data["name"] == "CS 101"
        assert data["description"] == "Introduction to Programming"
        assert data["color"] == "#3B82F6"
        assert data["is_archived"] is False
        assert "id" in data
        assert "created_at" in data
        assert data["notes_count"] == 0
        assert data["tasks_count"] == 0

    async def test_get_courses_requires_authentication(self, client: AsyncClient):
        """T074 [RED]: Test GET /api/v1/courses without authentication returns 401."""
        response = await client.get("/api/v1/courses")
        
        assert response.status_code == 401

    async def test_get_courses_with_auth(self, client: AsyncClient, db_session: AsyncSession):
        """Test GET /api/v1/courses returns user's courses."""
        # Register and login user
        user = await register_user(
            db=db_session,
            email="getcourses@example.com",
            password="password123",
            full_name="Get Courses User"
        )
        
        # Create courses
        await create_course(db=db_session, user_id=user.id, name="Course 1")
        await create_course(db=db_session, user_id=user.id, name="Course 2")
        
        # Login to get token
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": "getcourses@example.com", "password": "password123"}
        )
        token = login_response.json()["access_token"]
        
        # Get courses
        response = await client.get(
            "/api/v1/courses",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data) == 2
        assert data[0]["name"] in ["Course 1", "Course 2"]

    async def test_update_course_forbidden_if_not_owner(self, client: AsyncClient, db_session: AsyncSession):
        """T075 [RED]: Test PATCH /api/v1/courses/{id} forbidden if not owner."""
        # Register two users
        user1 = await register_user(
            db=db_session,
            email="owner@example.com",
            password="password123",
            full_name="Owner User"
        )
        user2 = await register_user(
            db=db_session,
            email="other@example.com",
            password="password123",
            full_name="Other User"
        )
        
        # Create course owned by user1
        course = await create_course(
            db=db_session,
            user_id=user1.id,
            name="Owner's Course"
        )
        
        # Login as user2
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": "other@example.com", "password": "password123"}
        )
        token = login_response.json()["access_token"]
        
        # Try to update user1's course as user2
        response = await client.patch(
            f"/api/v1/courses/{course.id}",
            json={"name": "Hacked Name"},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 403

    async def test_delete_course_returns_204(self, client: AsyncClient, db_session: AsyncSession):
        """T076 [RED]: Test DELETE /api/v1/courses/{id} returns 204."""
        # Register and login user
        user = await register_user(
            db=db_session,
            email="delete@example.com",
            password="password123",
            full_name="Delete User"
        )
        
        # Create course
        course = await create_course(
            db=db_session,
            user_id=user.id,
            name="Course to Delete"
        )
        
        # Login to get token
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": "delete@example.com", "password": "password123"}
        )
        token = login_response.json()["access_token"]
        
        # Delete course
        response = await client.delete(
            f"/api/v1/courses/{course.id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 204
        
        # Verify course is deleted
        get_response = await client.get(
            "/api/v1/courses",
            headers={"Authorization": f"Bearer {token}"}
        )
        courses = get_response.json()
        assert len(courses) == 0

    async def test_get_courses_filtered_by_archived(self, client: AsyncClient, db_session: AsyncSession):
        """Test GET /api/v1/courses?is_archived=false filters archived."""
        # Register and login user
        user = await register_user(
            db=db_session,
            email="archived@example.com",
            password="password123",
            full_name="Archived User"
        )
        
        # Create active and archived courses
        active = await create_course(db=db_session, user_id=user.id, name="Active")
        archived = await create_course(db=db_session, user_id=user.id, name="Archived")
        archived.is_archived = True
        await db_session.commit()
        
        # Login to get token
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": "archived@example.com", "password": "password123"}
        )
        token = login_response.json()["access_token"]
        
        # Get only active courses
        response = await client.get(
            "/api/v1/courses?is_archived=false",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data) == 1
        assert data[0]["name"] == "Active"
        assert data[0]["is_archived"] is False
