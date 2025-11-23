"""Course API endpoints."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.study_helper.api.deps import get_db, get_current_user
from src.study_helper.models.user import User
from src.study_helper.schemas.course import CourseCreate, CourseUpdate, CourseResponse
from src.study_helper.services.course import (
    create_course,
    get_courses,
    update_course,
    delete_course,
    get_course_with_counts,
)

router = APIRouter(prefix="/api/v1/courses", tags=["courses"])


@router.post("", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
async def create_course_endpoint(
    course_data: CourseCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> CourseResponse:
    """
    Create a new course.
    
    Requires authentication.
    
    Returns:
        CourseResponse with notes_count=0 and tasks_count=0
    """
    course = await create_course(
        db=db,
        user_id=current_user.id,
        name=course_data.name,
        description=course_data.description,
        color=course_data.color
    )
    
    # Add counts (new course has no notes/tasks)
    course.notes_count = 0
    course.tasks_count = 0
    
    return CourseResponse.model_validate(course)


@router.get("", response_model=List[CourseResponse])
async def get_courses_endpoint(
    is_archived: Optional[bool] = Query(None, description="Filter by archived status"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> List[CourseResponse]:
    """
    Get user's courses with optional archived filter.
    
    Requires authentication.
    
    Query params:
        is_archived: Optional filter (true/false/null for all)
        
    Returns:
        List of CourseResponse with notes_count and tasks_count
    """
    courses = await get_courses(
        db=db,
        user_id=current_user.id,
        is_archived=is_archived
    )
    
    # Add counts for each course
    from sqlalchemy import select, func
    from src.study_helper.models.note import Note
    from src.study_helper.models.task import Task
    
    course_responses = []
    for course in courses:
        # Get notes count
        notes_count_result = await db.execute(
            select(func.count(Note.id)).where(Note.course_id == course.id)
        )
        notes_count = notes_count_result.scalar() or 0
        
        # Get tasks count
        tasks_count_result = await db.execute(
            select(func.count(Task.id)).where(Task.course_id == course.id)
        )
        tasks_count = tasks_count_result.scalar() or 0
        
        # Add counts to course object
        course.notes_count = notes_count
        course.tasks_count = tasks_count
        
        course_responses.append(CourseResponse.model_validate(course))
    
    return course_responses


@router.patch("/{course_id}", response_model=CourseResponse)
async def update_course_endpoint(
    course_id: int,
    course_data: CourseUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> CourseResponse:
    """
    Update a course.
    
    Requires authentication and ownership.
    
    Returns:
        Updated CourseResponse
        
    Raises:
        404: Course not found
        403: Not authorized (not owner)
    """
    # Get update data (exclude unset fields)
    update_data = course_data.model_dump(exclude_unset=True)
    
    course = await update_course(
        db=db,
        course_id=course_id,
        user_id=current_user.id,
        **update_data
    )
    
    # Get counts
    course = await get_course_with_counts(
        db=db,
        course_id=course.id,
        user_id=current_user.id
    )
    
    return CourseResponse.model_validate(course)


@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_course_endpoint(
    course_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> None:
    """
    Delete a course (cascade deletes notes and tasks).
    
    Requires authentication and ownership.
    
    Returns:
        204 No Content on success
        
    Raises:
        404: Course not found
        403: Not authorized (not owner)
    """
    await delete_course(
        db=db,
        course_id=course_id,
        user_id=current_user.id
    )
