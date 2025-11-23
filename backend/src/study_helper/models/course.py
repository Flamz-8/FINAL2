"""Course model for organizing notes and tasks."""
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import String, DateTime, ForeignKey, Text, Boolean, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.study_helper.db.base import Base

if TYPE_CHECKING:
    from src.study_helper.models.user import User
    from src.study_helper.models.note import Note
    from src.study_helper.models.task import Task


class Course(Base):
    """Course model - organizational container for semester/subject."""
    
    __tablename__ = "courses"
    
    # Primary Key
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Foreign Key
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Attributes
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    color: Mapped[str] = mapped_column(String(7), default="#3B82F6", nullable=False)  # Hex color
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
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
    user: Mapped["User"] = relationship(back_populates="courses")
    notes: Mapped[List["Note"]] = relationship(
        back_populates="course",
        cascade="all, delete-orphan"
    )
    tasks: Mapped[List["Task"]] = relationship(
        back_populates="course",
        cascade="all, delete-orphan"
    )
    
    # Composite Index for filtering active courses (T054)
    __table_args__ = (
        Index("ix_courses_user_archived", "user_id", "is_archived"),
    )
    
    def __repr__(self) -> str:
        return f"<Course(id={self.id}, name='{self.name}', user_id={self.user_id})>"
