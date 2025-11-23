"""Note API endpoints (T109-T112)."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.study_helper.api.deps import get_db, get_current_user
from src.study_helper.models.user import User
from src.study_helper.schemas.note import NoteCreate, NoteUpdate, NoteResponse
from src.study_helper.services.note import (
    create_note,
    get_notes_by_course,
    update_note,
    delete_note,
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
    
    # Add empty linked_tasks (will be populated in US3)
    note.linked_tasks = []
    
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
    
    # Add empty linked_tasks to each note (will be populated in US3)
    note_responses = []
    for note in notes:
        note.linked_tasks = []
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
    
    # Add empty linked_tasks (will be populated in US3)
    note.linked_tasks = []
    
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
