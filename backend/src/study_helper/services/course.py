"""Course service for business logic."""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from fastapi import HTTPException, status

from src.study_helper.models.course import Course
from src.study_helper.models.note import Note
from src.study_helper.models.task import Task


async def create_course(
    db: AsyncSession,
    user_id: int,
    name: str,
    description: Optional[str] = None,
    color: str = "#3B82F6"
) -> Course:
    """
    Create a new course.
    
    Args:
        db: Database session
        user_id: Owner user ID
        name: Course name
        description: Optional description
        color: Hex color code
        
    Returns:
        Created Course instance
    """
    course = Course(
        user_id=user_id,
        name=name,
        description=description,
        color=color,
        is_archived=False
    )
    
    db.add(course)
    await db.commit()
    await db.refresh(course)
    
    return course


async def get_courses(
    db: AsyncSession,
    user_id: int,
    is_archived: Optional[bool] = None
) -> List[Course]:
    """
    Get user's courses with optional archived filter.
    
    Args:
        db: Database session
        user_id: Owner user ID
        is_archived: Optional filter for archived status
        
    Returns:
        List of Course instances
    """
    query = select(Course).where(Course.user_id == user_id)
    
    if is_archived is not None:
        query = query.where(Course.is_archived == is_archived)
    
    query = query.order_by(Course.created_at.desc())
    
    result = await db.execute(query)
    courses = result.scalars().all()
    
    return list(courses)


async def update_course(
    db: AsyncSession,
    course_id: int,
    user_id: int,
    name: Optional[str] = None,
    description: Optional[str] = None,
    color: Optional[str] = None,
    is_archived: Optional[bool] = None
) -> Course:
    """
    Update a course (ownership verification).
    
    Args:
        db: Database session
        course_id: Course ID to update
        user_id: Owner user ID for verification
        name: Optional new name
        description: Optional new description
        color: Optional new color
        is_archived: Optional archive status
        
    Returns:
        Updated Course instance
        
    Raises:
        HTTPException 404: Course not found
        HTTPException 403: User doesn't own course
    """
    # Get course
    result = await db.execute(
        select(Course).where(Course.id == course_id)
    )
    course = result.scalar_one_or_none()
    
    if course is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    # Verify ownership
    if course.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this course"
        )
    
    # Update fields
    if name is not None:
        course.name = name
    if description is not None:
        course.description = description
    if color is not None:
        course.color = color
    if is_archived is not None:
        course.is_archived = is_archived
    
    await db.commit()
    await db.refresh(course)
    
    return course


async def delete_course(
    db: AsyncSession,
    course_id: int,
    user_id: int
) -> None:
    """
    Delete a course (cascade deletes notes and tasks).
    
    Args:
        db: Database session
        course_id: Course ID to delete
        user_id: Owner user ID for verification
        
    Raises:
        HTTPException 404: Course not found
        HTTPException 403: User doesn't own course
    """
    # Get course
    result = await db.execute(
        select(Course).where(Course.id == course_id)
    )
    course = result.scalar_one_or_none()
    
    if course is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    # Verify ownership
    if course.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this course"
        )
    
    # Delete course (cascade will delete notes and tasks)
    await db.delete(course)
    await db.commit()


async def get_course_with_counts(
    db: AsyncSession,
    course_id: int,
    user_id: int
) -> Course:
    """
    Get a course with notes_count and tasks_count.
    
    Args:
        db: Database session
        course_id: Course ID
        user_id: Owner user ID for verification
        
    Returns:
        Course instance with counts
        
    Raises:
        HTTPException 404: Course not found
        HTTPException 403: User doesn't own course
    """
    # Get course
    result = await db.execute(
        select(Course).where(Course.id == course_id)
    )
    course = result.scalar_one_or_none()
    
    if course is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    # Verify ownership
    if course.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this course"
        )
    
    # Get counts
    notes_count_result = await db.execute(
        select(func.count(Note.id)).where(Note.course_id == course_id)
    )
    course.notes_count = notes_count_result.scalar() or 0
    
    tasks_count_result = await db.execute(
        select(func.count(Task.id)).where(Task.course_id == course_id)
    )
    course.tasks_count = tasks_count_result.scalar() or 0
    
    return course
