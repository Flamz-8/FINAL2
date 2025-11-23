"""Task API endpoints (T142-T145, T201)."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.study_helper.api.deps import get_db, get_current_user
from src.study_helper.models.user import User
from src.study_helper.schemas.task import TaskCreate, TaskUpdate, TaskResponse
from src.study_helper.services.task import (
    create_task,
    get_tasks_by_course,
    update_task,
    delete_task,
)

router = APIRouter(prefix="/api/v1", tags=["tasks"])


@router.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task_endpoint(
    task_data: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> TaskResponse:
    """
    Create a new task (T142).
    
    Requires authentication.
    
    Returns:
        TaskResponse with empty subtasks and linked_notes_count=0
    """
    task = await create_task(
        db=db,
        course_id=task_data.course_id,
        title=task_data.title,
        description=task_data.description,
        due_date=task_data.due_date,
        priority=task_data.priority
    )
    
    # Add empty subtasks and linked_notes_count from note_links (T201)
    task.subtasks = []
    task.linked_notes_count = len(task.note_links)
    
    return TaskResponse.model_validate(task)


@router.get("/courses/{course_id}/tasks", response_model=List[TaskResponse])
async def get_tasks_by_course_endpoint(
    course_id: int,
    completed: Optional[bool] = Query(None, description="Filter by completion status"),
    sort_by: str = Query("created_at", description="Field to sort by"),
    order: str = Query("asc", description="Sort order (asc/desc)"),
    limit: int = Query(50, description="Maximum number of tasks to return"),
    offset: int = Query(0, description="Number of tasks to skip"),
    view: str = Query("all", description="Time-based filter (all/today/week/upcoming)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> List[TaskResponse]:
    """
    Get tasks for a course with filtering, sorting, and pagination (T143, T178).
    
    Requires authentication.
    
    Query params:
        completed: Filter by completion status (true/false/null for all)
        sort_by: Field to sort by (created_at, due_date, priority)
        order: Sort order (asc/desc), default asc for oldest first (FR-029)
        limit: Maximum tasks to return (default 50)
        offset: Number of tasks to skip (default 0)
        view: Time-based filter (all/today/week/upcoming) [T178]
        
    Returns:
        List of TaskResponse sorted as specified
    """
    tasks = await get_tasks_by_course(
        db=db,
        course_id=course_id,
        completed=completed,
        sort_by=sort_by,
        order=order,
        limit=limit,
        offset=offset,
        view=view
    )
    
    # Add empty subtasks and linked_notes_count from note_links (T201)
    task_responses = []
    for task in tasks:
        task.subtasks = []
        task.linked_notes_count = len(task.note_links)
        task_responses.append(TaskResponse.model_validate(task))
    
    return task_responses


@router.patch("/tasks/{task_id}", response_model=TaskResponse)
async def update_task_endpoint(
    task_id: int,
    task_data: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> TaskResponse:
    """
    Update a task (T144).
    
    Requires authentication.
    
    Returns:
        Updated TaskResponse
        
    Raises:
        404: Task not found
    """
    # Get update data (exclude unset fields)
    update_data = task_data.model_dump(exclude_unset=True)
    
    task = await update_task(
        db=db,
        task_id=task_id,
        **update_data
    )
    
    # Add empty subtasks and linked_notes_count from note_links (T201)
    task.subtasks = []
    task.linked_notes_count = len(task.note_links)
    
    return TaskResponse.model_validate(task)


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task_endpoint(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> None:
    """
    Delete a task (T145).
    
    Requires authentication.
    
    Returns:
        204 No Content on success
        
    Raises:
        404: Task not found
    """
    await delete_task(
        db=db,
        task_id=task_id
    )


@router.get("/tasks/today", response_model=List[TaskResponse])
async def get_tasks_today(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> List[TaskResponse]:
    """
    Get all tasks due today across all courses (T179).
    
    Requires authentication.
    
    Returns:
        List of tasks due today from all user's courses
    """
    from src.study_helper.services.course import get_courses
    from src.study_helper.models.course import Course
    
    # Get all user's courses
    courses = await get_courses(db, user_id=current_user.id, is_archived=False)
    
    # Get today's tasks from each course
    all_tasks = []
    for course in courses:
        tasks = await get_tasks_by_course(
            db=db,
            course_id=course.id,
            view="today",
            sort_by="due_date",
            order="asc"
        )
        all_tasks.extend(tasks)
    
    # Convert to responses
    task_responses = []
    for task in all_tasks:
        task.subtasks = []
        task.linked_notes_count = len(task.note_links)
        task_responses.append(TaskResponse.model_validate(task))
    
    return task_responses


@router.get("/tasks/week", response_model=List[TaskResponse])
async def get_tasks_week(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> List[TaskResponse]:
    """
    Get all tasks due this week across all courses (T180).
    
    Requires authentication.
    
    Returns:
        List of tasks due this week from all user's courses
    """
    from src.study_helper.services.course import get_courses
    
    # Get all user's courses
    courses = await get_courses(db, user_id=current_user.id, is_archived=False)
    
    # Get this week's tasks from each course
    all_tasks = []
    for course in courses:
        tasks = await get_tasks_by_course(
            db=db,
            course_id=course.id,
            view="week",
            sort_by="due_date",
            order="asc"
        )
        all_tasks.extend(tasks)
    
    # Convert to responses
    task_responses = []
    for task in all_tasks:
        task.subtasks = []
        task.linked_notes_count = len(task.note_links)
        task_responses.append(TaskResponse.model_validate(task))
    
    return task_responses


@router.get("/tasks/upcoming", response_model=List[TaskResponse])
async def get_tasks_upcoming(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> List[TaskResponse]:
    """
    Get all upcoming tasks across all courses (T181).
    
    Requires authentication.
    
    Returns:
        List of upcoming tasks from all user's courses, sorted by due_date
    """
    from src.study_helper.services.course import get_courses
    
    # Get all user's courses
    courses = await get_courses(db, user_id=current_user.id, is_archived=False)
    
    # Get upcoming tasks from each course
    all_tasks = []
    for course in courses:
        tasks = await get_tasks_by_course(
            db=db,
            course_id=course.id,
            view="upcoming",
            sort_by="due_date",
            order="asc"
        )
        all_tasks.extend(tasks)
    
    # Convert to responses
    task_responses = []
    for task in all_tasks:
        task.subtasks = []
        task.linked_notes_count = len(task.note_links)
        task_responses.append(TaskResponse.model_validate(task))
    
    return task_responses

