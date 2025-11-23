"""Pydantic schemas for Task entity (T125-T128)."""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict, field_validator


class TaskCreate(BaseModel):
    """Schema for creating a new task."""
    
    course_id: int = Field(..., description="ID of the course this task belongs to")
    title: str = Field(default="", max_length=300, description="Task title")
    description: Optional[str] = Field(None, description="Task description")
    due_date: Optional[datetime] = Field(None, description="Task due date")
    priority: str = Field(default="medium", description="Task priority: low, medium, or high")
    
    @field_validator("title")
    @classmethod
    def generate_auto_title(cls, v: str) -> str:
        """T126: Generate placeholder title if empty (Clarification #5)."""
        if not v or v.strip() == "":
            timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            return f"Untitled Task - {timestamp}"
        return v
    
    @field_validator("priority")
    @classmethod
    def validate_priority(cls, v: str) -> str:
        """T124: Validate priority is low, medium, or high."""
        if v not in ["low", "medium", "high"]:
            raise ValueError("Priority must be 'low', 'medium', or 'high'")
        return v


class TaskUpdate(BaseModel):
    """Schema for updating a task - all fields optional (T127)."""
    
    title: Optional[str] = Field(None, max_length=300)
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: Optional[str] = None
    is_completed: Optional[bool] = Field(None, description="Mark task as completed")
    
    @field_validator("priority")
    @classmethod
    def validate_priority(cls, v: Optional[str]) -> Optional[str]:
        """Validate priority if provided."""
        if v is not None and v not in ["low", "medium", "high"]:
            raise ValueError("Priority must be 'low', 'medium', or 'high'")
        return v


class TaskResponse(BaseModel):
    """Schema for task response with subtasks and linked notes (T128)."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    course_id: int
    title: str
    description: Optional[str]
    due_date: Optional[datetime]
    priority: str
    status: str
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    subtasks: List[int] = Field(default_factory=list, description="IDs of subtasks (US4)")
    linked_notes_count: int = Field(default=0, description="Count of linked notes (US3)")
