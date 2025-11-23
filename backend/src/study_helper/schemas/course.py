"""Pydantic schemas for Course entity."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator
import re


class CourseCreate(BaseModel):
    """Schema for creating a new course."""
    
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    color: str = Field(default="#3B82F6", pattern=r"^#[0-9A-Fa-f]{6}$")
    
    @field_validator('color')
    @classmethod
    def validate_color(cls, v: str) -> str:
        """Validate hex color format."""
        if not re.match(r'^#[0-9A-Fa-f]{6}$', v):
            raise ValueError('Color must be a valid hex color code (e.g., #3B82F6)')
        return v


class CourseUpdate(BaseModel):
    """Schema for updating a course (all fields optional)."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    color: Optional[str] = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")
    is_archived: Optional[bool] = None
    
    @field_validator('color')
    @classmethod
    def validate_color(cls, v: Optional[str]) -> Optional[str]:
        """Validate hex color format if provided."""
        if v is not None and not re.match(r'^#[0-9A-Fa-f]{6}$', v):
            raise ValueError('Color must be a valid hex color code (e.g., #3B82F6)')
        return v


class CourseResponse(BaseModel):
    """Schema for course data in responses."""
    
    id: int
    user_id: int
    name: str
    description: Optional[str]
    color: str
    is_archived: bool
    created_at: datetime
    updated_at: datetime
    
    # Computed fields (populated by service layer)
    notes_count: int = 0
    tasks_count: int = 0
    
    model_config = {
        "from_attributes": True  # Enable ORM mode for SQLAlchemy models
    }
