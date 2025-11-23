"""Security utilities for password hashing and JWT token management."""
from datetime import datetime, timedelta
from typing import Optional
import bcrypt
from jose import jwt

from src.study_helper.core.config import settings

# JWT settings
ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    """
    Hash a plain text password using bcrypt.
    
    Args:
        password: Plain text password to hash
        
    Returns:
        Hashed password string (bcrypt format)
    """
    # Convert password to bytes and hash with bcrypt
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    # Return as string for database storage
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain text password against a hashed password.
    
    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password to compare against
        
    Returns:
        True if password matches, False otherwise
    """
    password_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def create_access_token(
    user_id: int,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT access token for authentication.
    
    Args:
        user_id: User ID to encode in the token
        expires_delta: Optional custom expiration time (defaults to 24 hours)
        
    Returns:
        Encoded JWT token string
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        # Default: 24 hours from settings
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {
        "sub": str(user_id),  # Subject: user ID
        "exp": expire,         # Expiration time
        "iat": datetime.utcnow()  # Issued at time
    }
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
