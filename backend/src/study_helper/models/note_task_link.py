"""NoteTaskLink model - many-to-many relationship between notes and tasks (T190-T192)."""
from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.study_helper.db.base import Base

if TYPE_CHECKING:
    from src.study_helper.models.note import Note
    from src.study_helper.models.task import Task


class NoteTaskLink(Base):
    """
    NoteTaskLink model - linking table for notes and tasks (T190).
    
    Per data-model.md § 2.5:
    - Many-to-many relationship between notes and tasks
    - Composite primary key (note_id, task_id) [T191]
    - Unique constraint to prevent duplicate links [T192]
    - Deleting note removes links but keeps tasks
    """
    
    __tablename__ = "note_task_links"
    
    # Composite primary key (T191)
    note_id: Mapped[int] = mapped_column(
        ForeignKey("notes.id", ondelete="CASCADE"),
        primary_key=True
    )
    task_id: Mapped[int] = mapped_column(
        ForeignKey("tasks.id", ondelete="CASCADE"),
        primary_key=True
    )
    
    # Unique constraint (T192) - enforced by composite PK but explicit for clarity
    __table_args__ = (
        UniqueConstraint("note_id", "task_id", name="uq_note_task_link"),
    )
    
    # Relationships
    note: Mapped["Note"] = relationship("Note", back_populates="task_links")
    task: Mapped["Task"] = relationship("Task", back_populates="note_links")
