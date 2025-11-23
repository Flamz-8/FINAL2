"""Contract tests for authentication API endpoints."""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from src.study_helper.services.auth import register_user


@pytest.mark.asyncio
class TestAuthAPI:
    """Test authentication API contract per api-specification.md."""

    async def test_register_success(self, client: AsyncClient):
        """Test POST /api/v1/auth/register with valid data returns 201."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "securepass123",
                "full_name": "New User"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        
        # Should return token and user data
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
        assert data["user"]["email"] == "newuser@example.com"
        assert data["user"]["full_name"] == "New User"
        assert "id" in data["user"]
        assert "created_at" in data["user"]
        
        # Should NOT return password
        assert "password" not in data["user"]
        assert "hashed_password" not in data["user"]

    async def test_register_duplicate_email_returns_409(self, client: AsyncClient, db_session: AsyncSession):
        """Test POST /api/v1/auth/register with duplicate email returns 409 Conflict."""
        # Register first user
        await register_user(
            db=db_session,
            email="existing@example.com",
            password="password123",
            full_name="Existing User"
        )
        
        # Attempt to register with same email
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "existing@example.com",
                "password": "different456",
                "full_name": "Different User"
            }
        )
        
        assert response.status_code == 409
        data = response.json()
        assert "detail" in data

    async def test_login_success_returns_token(self, client: AsyncClient, db_session: AsyncSession):
        """Test POST /api/v1/auth/login with valid credentials returns 200 with token."""
        # Register a user first
        await register_user(
            db=db_session,
            email="login@example.com",
            password="correctpassword",
            full_name="Login User"
        )
        
        # Login with correct credentials
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "login@example.com",
                "password": "correctpassword"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should return token and user data
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
        assert data["user"]["email"] == "login@example.com"
        
        # Should NOT return password
        assert "password" not in data["user"]

    async def test_login_invalid_credentials_returns_401(self, client: AsyncClient, db_session: AsyncSession):
        """Test POST /api/v1/auth/login with invalid password returns 401 Unauthorized."""
        # Register a user first
        await register_user(
            db=db_session,
            email="login2@example.com",
            password="correctpassword",
            full_name="Login User 2"
        )
        
        # Login with wrong password
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "login2@example.com",
                "password": "wrongpassword"
            }
        )
        
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

    async def test_login_nonexistent_email_returns_401(self, client: AsyncClient):
        """Test POST /api/v1/auth/login with non-existent email returns 401."""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "anypassword"
            }
        )
        
        assert response.status_code == 401

    async def test_register_invalid_email_returns_422(self, client: AsyncClient):
        """Test POST /api/v1/auth/register with invalid email format returns 422."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "not-an-email",
                "password": "securepass123",
                "full_name": "Test User"
            }
        )
        
        assert response.status_code == 422  # Pydantic validation error

    async def test_register_password_too_short_returns_422(self, client: AsyncClient):
        """Test POST /api/v1/auth/register with password < 8 chars returns 422."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "password": "short",  # Only 5 chars
                "full_name": "Test User"
            }
        )
        
        assert response.status_code == 422  # Pydantic validation error
