"""Pydantic schemas for user authentication and responses."""
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, field_validator


class UserRegister(BaseModel):
    """Schema for user registration."""
    
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=1, max_length=200)


class UserResponse(BaseModel):
    """Schema for user data in responses (excludes password)."""
    
    id: int
    email: str
    full_name: str
    created_at: datetime
    
    model_config = {
        "from_attributes": True  # Enable ORM mode for SQLAlchemy models
    }


class UserLogin(BaseModel):
    """Schema for user login credentials."""
    
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Schema for authentication token response."""
    
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
