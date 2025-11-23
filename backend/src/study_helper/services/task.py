"""Task service layer for business logic (T133-T137, T171-T173, T201-T202)."""
from typing import List, Optional, Literal
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc, asc
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from src.study_helper.models.task import Task
from src.study_helper.utils.date_filters import is_today, is_this_week, is_upcoming


async def create_task(
    db: AsyncSession,
    course_id: int,
    title: str,
    description: Optional[str] = None,
    due_date: Optional[datetime] = None,
    priority: str = "medium"
) -> Task:
    """
    Create a new task (T133, T201).
    
    Eagerly loads note_links to prevent lazy loading issues (T202).
    
    Args:
        db: Database session
        course_id: ID of the course this task belongs to
        title: Task title (auto-generated if empty via schema validation)
        description: Optional task description
        due_date: Optional due date
        priority: Priority level (low/medium/high)
        
    Returns:
        Task: Created task instance with note_links loaded
    """
    task = Task(
        course_id=course_id,
        title=title,
        description=description,
        due_date=due_date,
        priority=priority,
        status="pending"
    )
    
    db.add(task)
    await db.commit()
    
    # Refresh with eager loading (T202)
    await db.refresh(task, attribute_names=["note_links"])
    
    return task


async def get_tasks_by_course(
    db: AsyncSession,
    course_id: int,
    completed: Optional[bool] = None,
    sort_by: str = "created_at",
    order: str = "asc",
    limit: int = 50,
    offset: int = 0,
    view: Optional[Literal["all", "today", "week", "upcoming"]] = "all"
) -> List[Task]:
    """
    Get tasks for a course with filtering, sorting, and pagination (T134, T171-T173, T201-T202).
    
    Uses selectinload() to eagerly load note_links and prevent N+1 queries (T202).
    
    Args:
        db: Database session
        course_id: ID of the course
        completed: Filter by completion status (None = all)
        sort_by: Field to sort by (created_at, due_date, priority)
        order: Sort order ('asc' or 'desc'), default 'asc' for oldest first (FR-029)
        limit: Maximum number of tasks to return (default 50)
        offset: Number of tasks to skip
        view: Time-based filter (all/today/week/upcoming) [T171]
        
    Returns:
        List[Task]: List of tasks with note_links eagerly loaded
    """
    # Build query with eager loading (T202 - prevent N+1)
    query = (
        select(Task)
        .where(Task.course_id == course_id)
        .options(selectinload(Task.note_links))  # T202: Prevent N+1 queries
    )
    
    # Filter by completed status
    if completed is not None:
        status_value = "completed" if completed else "pending"
        query = query.where(Task.status == status_value)
    
    # Apply pagination
    query = query.limit(limit).offset(offset)
    
    result = await db.execute(query)
    tasks = list(result.scalars().all())
    
    # Apply time-based filtering in Python (T172)
    if view != "all":
        filtered_tasks = []
        for task in tasks:
            if task.due_date is None:
                # Tasks without due dates excluded from time views (T170)
                continue
                
            task_date = task.due_date.date() if isinstance(task.due_date, datetime) else task.due_date
            
            if view == "today" and is_today(task_date):
                filtered_tasks.append(task)
            elif view == "week" and is_this_week(task_date):
                filtered_tasks.append(task)
            elif view == "upcoming" and is_upcoming(task_date):
                filtered_tasks.append(task)
        
        tasks = filtered_tasks
    
    # Apply sorting after filtering (T173)
    if sort_by == "due_date":
        tasks.sort(key=lambda t: t.due_date if t.due_date else datetime.max, reverse=(order == "desc"))
    elif sort_by == "priority":
        priority_order = {"high": 0, "medium": 1, "low": 2}
        tasks.sort(key=lambda t: priority_order.get(t.priority, 3), reverse=(order == "desc"))
    else:  # created_at or default
        tasks.sort(key=lambda t: t.created_at, reverse=(order == "desc"))
    
    return tasks


async def update_task(
    db: AsyncSession,
    task_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    due_date: Optional[datetime] = None,
    priority: Optional[str] = None,
    is_completed: Optional[bool] = None
) -> Task:
    """
    Update a task (T135).
    
    If is_completed is set to True, sets status to 'completed' and completed_at timestamp.
    If is_completed is set to False, sets status to 'pending' and clears completed_at.
    
    Args:
        db: Database session
        task_id: ID of the task to update
        title: New title (optional)
        description: New description (optional)
        due_date: New due date (optional)
        priority: New priority (optional)
        is_completed: Mark as completed/pending (optional)
        
    Returns:
        Task: Updated task instance
        
    Raises:
        HTTPException: 404 if task not found
    """
    # Get task
    result = await db.execute(
        select(Task).where(Task.id == task_id)
    )
    task = result.scalar_one_or_none()
    
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found"
        )
    
    # Update fields
    if title is not None:
        task.title = title
    if description is not None:
        task.description = description
    if due_date is not None:
        task.due_date = due_date
    if priority is not None:
        task.priority = priority
    
    # Handle completion status
    if is_completed is not None:
        if is_completed:
            task.status = "completed"
            task.completed_at = datetime.utcnow()
        else:
            task.status = "pending"
            task.completed_at = None
    
    await db.commit()
    await db.refresh(task, attribute_names=["note_links"])
    
    return task


async def delete_task(
    db: AsyncSession,
    task_id: int
) -> None:
    """
    Delete a task (T136).
    
    Note: Subtask promotion deferred to US4.
    
    Args:
        db: Database session
        task_id: ID of the task to delete
        
    Raises:
        HTTPException: 404 if task not found
    """
    # Get task
    result = await db.execute(
        select(Task).where(Task.id == task_id)
    )
    task = result.scalar_one_or_none()
    
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found"
        )
    
    await db.delete(task)
    await db.commit()
