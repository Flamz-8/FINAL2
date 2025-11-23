"""Pydantic schemas for Note entity."""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class NoteCreate(BaseModel):
    """Schema for creating a new note (T092-T093)."""
    
    course_id: int = Field(..., description="ID of the course this note belongs to")
    title: str = Field(..., max_length=300, description="Note title")
    content: str = Field(..., max_length=50000, description="Note content in Markdown format")
    tags: Optional[str] = Field(None, max_length=500, description="Comma-separated tags")


class NoteUpdate(BaseModel):
    """Schema for updating a note - all fields optional (T094)."""
    
    title: Optional[str] = Field(None, max_length=300)
    content: Optional[str] = Field(None, max_length=50000)
    tags: Optional[str] = Field(None, max_length=500)


class NoteResponse(BaseModel):
    """Schema for note response with linked tasks (T095)."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    course_id: int
    title: str
    content: str
    tags: Optional[str]
    created_at: datetime
    updated_at: datetime
    linked_tasks: List[int] = Field(default_factory=list, description="IDs of linked tasks (US3)")
