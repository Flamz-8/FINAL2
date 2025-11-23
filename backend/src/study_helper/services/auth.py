"""Authentication service for user registration and authentication."""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.study_helper.models.user import User
from src.study_helper.core.security import hash_password, verify_password


async def register_user(
    db: AsyncSession,
    email: str,
    password: str,
    full_name: str
) -> User:
    """
    Register a new user with hashed password.
    
    Args:
        db: Database session
        email: User's email address
        password: Plain text password (will be hashed)
        full_name: User's full name
        
    Returns:
        Created User instance
        
    Raises:
        IntegrityError: If email already exists (unique constraint)
    """
    # Hash the password
    hashed_password = hash_password(password)
    
    # Create new user
    user = User(
        email=email,
        hashed_password=hashed_password,
        full_name=full_name
    )
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    return user


async def authenticate_user(
    db: AsyncSession,
    email: str,
    password: str
) -> Optional[User]:
    """
    Authenticate a user by email and password.
    
    Args:
        db: Database session
        email: User's email address
        password: Plain text password to verify
        
    Returns:
        User instance if authentication successful, None otherwise
    """
    # Find user by email
    result = await db.execute(
        select(User).where(User.email == email)
    )
    user = result.scalar_one_or_none()
    
    if user is None:
        return None
    
    # Verify password
    if not verify_password(password, user.hashed_password):
        return None
    
    return user
