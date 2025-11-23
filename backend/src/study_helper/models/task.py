"""Task model for todo items with due dates and priority."""
from datetime import datetime
from typing import Optional, TYPE_CHECKING, List
from enum import Enum
from sqlalchemy import String, DateTime, ForeignKey, Text, Boolean, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.study_helper.db.base import Base

if TYPE_CHECKING:
    from src.study_helper.models.course import Course
    from src.study_helper.models.note_task_link import NoteTaskLink


class TaskPriority(str, Enum):
    """Task priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TaskStatus(str, Enum):
    """Task completion status."""
    PENDING = "pending"
    COMPLETED = "completed"


class Task(Base):
    """Task model - todo item with due dates and priority."""
    
    __tablename__ = "tasks"
    
    # Primary Key
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Foreign Key
    course_id: Mapped[int] = mapped_column(
        ForeignKey("courses.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Attributes
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    due_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, index=True)
    priority: Mapped[str] = mapped_column(String(10), default="medium", nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )
    
    # Relationships
    course: Mapped["Course"] = relationship(back_populates="tasks")
    note_links: Mapped[List["NoteTaskLink"]] = relationship(
        "NoteTaskLink",
        back_populates="task",
        cascade="all, delete-orphan"
    )
    
    # Composite Indexes for task queries (T086)
    __table_args__ = (
        Index("ix_tasks_course_due", "course_id", "due_date"),
        Index("ix_tasks_course_created", "course_id", "created_at"),
    )
    
    def __repr__(self) -> str:
        return f"<Task(id={self.id}, title='{self.title[:30]}...', course_id={self.course_id})>"
