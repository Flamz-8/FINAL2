"""Note service layer for business logic (T100-T104)."""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc, asc
from fastapi import HTTPException, status

from src.study_helper.models.note import Note


async def create_note(
    db: AsyncSession,
    course_id: int,
    title: str,
    content: str,
    tags: Optional[str] = None
) -> Note:
    """
    Create a new note (T100).
    
    Args:
        db: Database session
        course_id: ID of the course this note belongs to
        title: Note title
        content: Note content (Markdown)
        tags: Optional comma-separated tags
        
    Returns:
        Note: Created note instance
    """
    note = Note(
        course_id=course_id,
        title=title,
        content=content,
        tags=tags
    )
    
    db.add(note)
    await db.commit()
    await db.refresh(note)
    
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
    Get notes for a course with sorting and pagination (T101, T104).
    
    Args:
        db: Database session
        course_id: ID of the course
        sort_by: Field to sort by (created_at, updated_at, title)
        order: Sort order ('asc' or 'desc'), default 'desc' for newest first (FR-016)
        limit: Maximum number of notes to return (default 50)
        offset: Number of notes to skip
        
    Returns:
        List[Note]: List of notes sorted as specified
    """
    # Build query
    query = select(Note).where(Note.course_id == course_id)
    
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
    Update a note (T102).
    
    The updated_at timestamp is automatically updated by SQLAlchemy's onupdate.
    
    Args:
        db: Database session
        note_id: ID of the note to update
        title: New title (optional)
        content: New content (optional)
        tags: New tags (optional)
        
    Returns:
        Note: Updated note instance
        
    Raises:
        HTTPException: 404 if note not found
    """
    # Get note
    result = await db.execute(
        select(Note).where(Note.id == note_id)
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
    await db.refresh(note)
    
    return note


async def delete_note(
    db: AsyncSession,
    note_id: int
) -> None:
    """
    Delete a note (T103).
    
    Note: In US3, this will also remove note-task links but keep the tasks.
    
    Args:
        db: Database session
        note_id: ID of the note to delete
        
    Raises:
        HTTPException: 404 if note not found
    """
    # Get note
    result = await db.execute(
        select(Note).where(Note.id == note_id)
    )
    note = result.scalar_one_or_none()
    
    if note is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Note with id {note_id} not found"
        )
    
    await db.delete(note)
    await db.commit()
