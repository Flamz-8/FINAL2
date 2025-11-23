"""Note API endpoints (T109-T112, T200, T206-T208)."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from src.study_helper.api.deps import get_db, get_current_user
from src.study_helper.models.user import User
from src.study_helper.schemas.note import NoteCreate, NoteUpdate, NoteResponse
from src.study_helper.schemas.note_task_link import NoteTaskLinkCreate, NoteTaskLinkResponse
from src.study_helper.services.note import (
    create_note,
    get_notes_by_course,
    update_note,
    delete_note,
    link_note_to_task,
    unlink_note_from_task,
)

router = APIRouter(prefix="/api/v1", tags=["notes"])


@router.post("/notes", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
async def create_note_endpoint(
    note_data: NoteCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> NoteResponse:
    """
    Create a new note (T109).
    
    Requires authentication.
    
    Returns:
        NoteResponse with empty linked_tasks list
    """
    note = await create_note(
        db=db,
        course_id=note_data.course_id,
        title=note_data.title,
        content=note_data.content,
        tags=note_data.tags
    )
    
    # Populate linked_tasks from task_links relationship (T200)
    note.linked_tasks = [link.task_id for link in note.task_links]
    
    return NoteResponse.model_validate(note)


@router.get("/courses/{course_id}/notes", response_model=List[NoteResponse])
async def get_notes_by_course_endpoint(
    course_id: int,
    sort_by: str = Query("created_at", description="Field to sort by"),
    order: str = Query("desc", description="Sort order (asc/desc)"),
    limit: int = Query(50, description="Maximum number of notes to return"),
    offset: int = Query(0, description="Number of notes to skip"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> List[NoteResponse]:
    """
    Get notes for a course with sorting and pagination (T110).
    
    Requires authentication.
    
    Query params:
        sort_by: Field to sort by (created_at, updated_at, title)
        order: Sort order (asc/desc), default desc for newest first (FR-016)
        limit: Maximum notes to return (default 50)
        offset: Number of notes to skip (default 0)
        
    Returns:
        List of NoteResponse sorted as specified
    """
    notes = await get_notes_by_course(
        db=db,
        course_id=course_id,
        sort_by=sort_by,
        order=order,
        limit=limit,
        offset=offset
    )
    
    # Populate linked_tasks from task_links relationship (T200)
    note_responses = []
    for note in notes:
        note.linked_tasks = [link.task_id for link in note.task_links]
        note_responses.append(NoteResponse.model_validate(note))
    
    return note_responses


@router.patch("/notes/{note_id}", response_model=NoteResponse)
async def update_note_endpoint(
    note_id: int,
    note_data: NoteUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> NoteResponse:
    """
    Update a note (T111).
    
    Requires authentication.
    
    Returns:
        Updated NoteResponse
        
    Raises:
        404: Note not found
    """
    # Get update data (exclude unset fields)
    update_data = note_data.model_dump(exclude_unset=True)
    
    note = await update_note(
        db=db,
        note_id=note_id,
        **update_data
    )
    
    # Populate linked_tasks from task_links relationship (T200)
    note.linked_tasks = [link.task_id for link in note.task_links]
    
    return NoteResponse.model_validate(note)


@router.delete("/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note_endpoint(
    note_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> None:
    """
    Delete a note (T112).
    
    Requires authentication.
    
    Returns:
        204 No Content on success
        
    Raises:
        404: Note not found
    """
    await delete_note(
        db=db,
        note_id=note_id
    )


@router.post("/notes/{note_id}/link-task", response_model=NoteTaskLinkResponse, status_code=status.HTTP_201_CREATED)
async def link_note_to_task_endpoint(
    note_id: int,
    link_data: NoteTaskLinkCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> NoteTaskLinkResponse:
    """
    Link a note to a task (T206 [GREEN]).
    
    Creates a many-to-many relationship between the note and task.
    
    Args:
        note_id: ID of the note
        link_data: Contains task_id to link
        
    Returns:
        NoteTaskLinkResponse with note_id and task_id
        
    Raises:
        404: Note or task not found (T208)
        409: Link already exists (duplicate)
    """
    try:
        link = await link_note_to_task(
            db=db,
            note_id=note_id,
            task_id=link_data.task_id
        )
        return NoteTaskLinkResponse.model_validate(link)
    except IntegrityError:
        # Rollback the failed transaction
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Note {note_id} and task {link_data.task_id} are already linked"
        )


@router.delete("/notes/{note_id}/link-task/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def unlink_note_from_task_endpoint(
    note_id: int,
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> None:
    """
    Unlink a note from a task (T207 [GREEN]).
    
    Removes the many-to-many relationship between the note and task.
    
    Args:
        note_id: ID of the note
        task_id: ID of the task
        
    Returns:
        204 No Content on success
        
    Raises:
        404: Link not found (T208)
    """
    await unlink_note_from_task(
        db=db,
        note_id=note_id,
        task_id=task_id
    )
