"""Note model for storing rich text content."""
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, DateTime, ForeignKey, Text, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.study_helper.db.base import Base

if TYPE_CHECKING:
    from src.study_helper.models.course import Course


class Note(Base):
    """Note model - rich text content with timestamps."""
    
    __tablename__ = "notes"
    
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
    content: Mapped[str] = mapped_column(Text, nullable=False)  # Markdown format
    tags: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)  # Comma-separated
    
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
    course: Mapped["Course"] = relationship(back_populates="notes")
    
    # Composite Index for sorting notes in course (T086)
    __table_args__ = (
        Index("ix_notes_course_created", "course_id", "created_at"),
    )
    
    def __repr__(self) -> str:
        return f"<Note(id={self.id}, title='{self.title[:30]}...', course_id={self.course_id})>"
