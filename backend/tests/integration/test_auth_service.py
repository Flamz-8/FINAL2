"""Integration tests for auth service (database interaction)."""
import pytest
from sqlalchemy.exc import IntegrityError
from src.study_helper.services.auth import register_user, authenticate_user
from src.study_helper.models.user import User


@pytest.mark.asyncio
class TestAuthService:
    """Test authentication service functions with database."""

    async def test_register_user_success(self, db_session):
        """Test successful user registration."""
        user = await register_user(
            db=db_session,
            email="newuser@example.com",
            password="securepass123",
            full_name="New User"
        )
        
        assert user.id is not None
        assert user.email == "newuser@example.com"
        assert user.full_name == "New User"
        # Password should be hashed, not plain text
        assert user.hashed_password != "securepass123"
        assert user.hashed_password.startswith("$2b$")  # bcrypt hash
        assert user.created_at is not None

    async def test_register_duplicate_email_fails(self, db_session):
        """Test registration with duplicate email raises IntegrityError."""
        # Create first user
        await register_user(
            db=db_session,
            email="duplicate@example.com",
            password="password123",
            full_name="First User"
        )
        
        # Attempt to create second user with same email
        with pytest.raises(IntegrityError):
            await register_user(
                db=db_session,
                email="duplicate@example.com",  # Same email
                password="different456",
                full_name="Second User"
            )

    async def test_authenticate_user_valid_credentials(self, db_session):
        """Test authentication with valid email and password."""
        # Register a user
        registered_user = await register_user(
            db=db_session,
            email="auth@example.com",
            password="correctpassword",
            full_name="Auth User"
        )
        
        # Authenticate with correct credentials
        authenticated_user = await authenticate_user(
            db=db_session,
            email="auth@example.com",
            password="correctpassword"
        )
        
        assert authenticated_user is not None
        assert authenticated_user.id == registered_user.id
        assert authenticated_user.email == "auth@example.com"

    async def test_authenticate_user_invalid_password_returns_none(self, db_session):
        """Test authentication fails with incorrect password."""
        # Register a user
        await register_user(
            db=db_session,
            email="auth2@example.com",
            password="correctpassword",
            full_name="Auth User 2"
        )
        
        # Authenticate with wrong password
        result = await authenticate_user(
            db=db_session,
            email="auth2@example.com",
            password="wrongpassword"
        )
        
        assert result is None

    async def test_authenticate_user_nonexistent_email_returns_none(self, db_session):
        """Test authentication fails with non-existent email."""
        result = await authenticate_user(
            db=db_session,
            email="nonexistent@example.com",
            password="anypassword"
        )
        
        assert result is None
