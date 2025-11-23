"""Note service layer for business logic (T100-T104, T198-T202)."""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc, asc
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from src.study_helper.models.note import Note
from src.study_helper.models.note_task_link import NoteTaskLink


async def create_note(
    db: AsyncSession,
    course_id: int,
    title: str,
    content: str,
    tags: Optional[str] = None
) -> Note:
    """
    Create a new note (T100, T200).
    
    Eagerly loads task_links to prevent lazy loading issues (T202).
    
    Args:
        db: Database session
        course_id: ID of the course this note belongs to
        title: Note title
        content: Note content (Markdown)
        tags: Optional comma-separated tags
        
    Returns:
        Note: Created note instance with task_links loaded
    """
    note = Note(
        course_id=course_id,
        title=title,
        content=content,
        tags=tags
    )
    
    db.add(note)
    await db.commit()
    
    # Refresh with eager loading (T202)
    await db.refresh(note, attribute_names=["task_links"])
    
    return note


async def get_notes_by_course(
    db: AsyncSession,
    course_id: int,
    sort_by: str = "created_at",
    order: str = "desc",
    limit: int = 50,
    offset: int = 0
) -> List[Note]:
    """
    Get notes for a course with sorting and pagination (T101, T104, T200, T202).
    
    Uses selectinload() to eagerly load task_links and prevent N+1 queries (T202).
    
    Args:
        db: Database session
        course_id: ID of the course
        sort_by: Field to sort by (created_at, updated_at, title)
        order: Sort order ('asc' or 'desc'), default 'desc' for newest first (FR-016)
        limit: Maximum number of notes to return (default 50)
        offset: Number of notes to skip
        
    Returns:
        List[Note]: List of notes with task_links eagerly loaded
    """
    # Build query with eager loading (T202 - prevent N+1)
    query = (
        select(Note)
        .where(Note.course_id == course_id)
        .options(selectinload(Note.task_links))  # T202: Prevent N+1 queries
    )
    
    # Apply sorting
    sort_column = getattr(Note, sort_by, Note.created_at)
    if order == "asc":
        query = query.order_by(asc(sort_column))
    else:
        query = query.order_by(desc(sort_column))
    
    # Apply pagination
    query = query.limit(limit).offset(offset)
    
    result = await db.execute(query)
    notes = result.scalars().all()
    
    return list(notes)


async def update_note(
    db: AsyncSession,
    note_id: int,
    title: Optional[str] = None,
    content: Optional[str] = None,
    tags: Optional[str] = None
) -> Note:
    """
    Update a note (T102, T200).
    
    The updated_at timestamp is automatically updated by SQLAlchemy's onupdate.
    Eagerly loads task_links to prevent lazy loading issues (T202).
    
    Args:
        db: Database session
        note_id: ID of the note to update
        title: New title (optional)
        content: New content (optional)
        tags: New tags (optional)
        
    Returns:
        Note: Updated note instance with task_links loaded
        
    Raises:
        HTTPException: 404 if note not found
    """
    # Get note with eager loading (T202)
    result = await db.execute(
        select(Note)
        .where(Note.id == note_id)
        .options(selectinload(Note.task_links))
    )
    note = result.scalar_one_or_none()
    
    if note is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Note with id {note_id} not found"
        )
    
    # Update fields
    if title is not None:
        note.title = title
    if content is not None:
        note.content = content
    if tags is not None:
        note.tags = tags
    
    await db.commit()
    await db.refresh(note, attribute_names=["task_links"])
    
    return note


async def delete_note(
    db: AsyncSession,
    note_id: int
) -> None:
    """
    Delete a note (T103, T197).
    
    Removes note and cascades to delete note-task links but keeps tasks (T197).
    
    Args:
        db: Database session
        note_id: ID of the note to delete
        
    Raises:
        HTTPException: 404 if note not found
    """
    # Get note with task_links loaded for cascade delete (T197)
    result = await db.execute(
        select(Note)
        .where(Note.id == note_id)
        .options(selectinload(Note.task_links))
    )
    note = result.scalar_one_or_none()
    
    if note is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Note with id {note_id} not found"
        )
    
    await db.delete(note)
    await db.commit()


async def link_note_to_task(
    db: AsyncSession,
    note_id: int,
    task_id: int
) -> NoteTaskLink:
    """
    Link a note to a task (T198 [GREEN]).
    
    Creates a many-to-many relationship between a note and a task.
    
    Args:
        db: Database session
        note_id: ID of the note
        task_id: ID of the task
        
    Returns:
        NoteTaskLink: The created link
        
    Raises:
        IntegrityError: If link already exists (duplicate)
    """
    link = NoteTaskLink(note_id=note_id, task_id=task_id)
    db.add(link)
    await db.commit()
    await db.refresh(link)
    return link


async def unlink_note_from_task(
    db: AsyncSession,
    note_id: int,
    task_id: int
) -> None:
    """
    Unlink a note from a task (T199 [GREEN]).
    
    Removes the many-to-many relationship between a note and a task.
    
    Args:
        db: Database session
        note_id: ID of the note
        task_id: ID of the task
        
    Raises:
        HTTPException: 404 if link not found
    """
    result = await db.execute(
        select(NoteTaskLink).where(
            NoteTaskLink.note_id == note_id,
            NoteTaskLink.task_id == task_id
        )
    )
    link = result.scalar_one_or_none()
    
    if link is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Link between note {note_id} and task {task_id} not found"
        )
    
    await db.delete(link)
    await db.commit()
