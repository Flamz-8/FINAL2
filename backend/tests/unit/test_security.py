"""Unit tests for security module (password hashing, JWT)."""
import pytest
from datetime import datetime, timedelta
from src.study_helper.core.security import (
    hash_password,
    verify_password,
    create_access_token,
)


class TestPasswordHashing:
    """Test password hashing and verification."""

    def test_hash_password(self):
        """Test that passwords are hashed correctly."""
        password = "mysecurepassword123"
        hashed = hash_password(password)
        
        # Hashed password should not equal plain password
        assert hashed != password
        # Hashed password should be a bcrypt hash (starts with $2b$)
        assert hashed.startswith("$2b$")
        # Hash should be consistent length (60 chars for bcrypt)
        assert len(hashed) == 60

    def test_verify_password(self):
        """Test password verification with correct password."""
        password = "correctpassword"
        hashed = hash_password(password)
        
        # Correct password should verify
        assert verify_password(password, hashed) is True

    def test_verify_password_fails_with_wrong_password(self):
        """Test password verification fails with incorrect password."""
        password = "correctpassword"
        hashed = hash_password(password)
        
        # Wrong password should not verify
        assert verify_password("wrongpassword", hashed) is False


class TestJWT:
    """Test JWT token creation and verification."""

    def test_create_access_token(self):
        """Test JWT access token creation."""
        user_id = 123
        token = create_access_token(user_id=user_id)
        
        # Token should be a string
        assert isinstance(token, str)
        # Token should have 3 parts (header.payload.signature)
        assert len(token.split('.')) == 3

    def test_create_access_token_with_custom_expiry(self):
        """Test JWT token creation with custom expiration."""
        user_id = 456
        expires_delta = timedelta(hours=1)
        token = create_access_token(user_id=user_id, expires_delta=expires_delta)
        
        # Token should be created successfully
        assert isinstance(token, str)
        assert len(token.split('.')) == 3
