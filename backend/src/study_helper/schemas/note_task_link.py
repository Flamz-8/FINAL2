"""Pydantic schemas for NoteTaskLink entity (T206-T207)."""
from pydantic import BaseModel, Field, ConfigDict


class NoteTaskLinkCreate(BaseModel):
    """Schema for creating a note-task link."""
    
    task_id: int = Field(..., description="ID of the task to link to the note")


class NoteTaskLinkResponse(BaseModel):
    """Schema for note-task link response."""
    
    model_config = ConfigDict(from_attributes=True)
    
    note_id: int
    task_id: int
