"""Integration tests for Note service layer (T096-T099, T194-T197)."""
import pytest
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from src.study_helper.services.auth import register_user
from src.study_helper.services.course import create_course
from src.study_helper.services.note import (
    create_note,
    get_notes_by_course,
    update_note,
    delete_note,
)
from src.study_helper.services.task import create_task
from src.study_helper.models.note import Note


@pytest.mark.asyncio
class TestNoteService:
    """Test Note service layer."""
    
    async def test_create_note(self, db_session: AsyncSession):
        """T096 [RED]: Test creating a note."""
        # Create user and course
        user = await register_user(
            db_session,
            email="test@example.com",
            password="password123",
            full_name="Test User"
        )
        course = await create_course(
            db_session,
            user_id=user.id,
            name="CS 101",
            color="#3B82F6"
        )
        
        # Create note
        note = await create_note(
            db=db_session,
            course_id=course.id,
            title="Lecture 1 Notes",
            content="# Introduction\n\nKey concepts...",
            tags="intro,basics"
        )
        
        assert note.id is not None
        assert note.course_id == course.id
        assert note.title == "Lecture 1 Notes"
        assert note.content == "# Introduction\n\nKey concepts..."
        assert note.tags == "intro,basics"
        assert note.created_at is not None
        assert note.updated_at is not None
    
    async def test_get_notes_by_course_sorted_newest_first(self, db_session: AsyncSession):
        """T097 [RED]: Test getting notes sorted by created_at desc (FR-016 default)."""
        # Create user and course
        user = await register_user(
            db_session,
            email="test@example.com",
            password="password123",
            full_name="Test User"
        )
        course = await create_course(
            db_session,
            user_id=user.id,
            name="CS 101",
            color="#3B82F6"
        )
        
        # Create multiple notes
        note1 = await create_note(
            db_session,
            course_id=course.id,
            title="Note 1",
            content="First note"
        )
        note2 = await create_note(
            db_session,
            course_id=course.id,
            title="Note 2",
            content="Second note"
        )
        note3 = await create_note(
            db_session,
            course_id=course.id,
            title="Note 3",
            content="Third note"
        )
        
        # Get notes (default sort: newest first)
        notes = await get_notes_by_course(
            db=db_session,
            course_id=course.id
        )
        
        assert len(notes) == 3
        # Newest first (note3, note2, note1)
        assert notes[0].title == "Note 3"
        assert notes[1].title == "Note 2"
        assert notes[2].title == "Note 1"
    
    async def test_update_note_updates_updated_at_timestamp(self, db_session: AsyncSession):
        """T098 [RED]: Test updating a note updates the updated_at timestamp."""
        # Create user, course, and note
        user = await register_user(
            db_session,
            email="test@example.com",
            password="password123",
            full_name="Test User"
        )
        course = await create_course(
            db_session,
            user_id=user.id,
            name="CS 101",
            color="#3B82F6"
        )
        note = await create_note(
            db_session,
            course_id=course.id,
            title="Original Title",
            content="Original content"
        )
        
        original_updated_at = note.updated_at
        
        # Wait a moment to ensure timestamp difference
        import asyncio
        await asyncio.sleep(0.1)
        
        # Update note
        updated_note = await update_note(
            db=db_session,
            note_id=note.id,
            title="Updated Title",
            content="Updated content"
        )
        
        assert updated_note.title == "Updated Title"
        assert updated_note.content == "Updated content"
        assert updated_note.updated_at > original_updated_at
    
    async def test_delete_note_succeeds(self, db_session: AsyncSession):
        """T099 [RED]: Test deleting a note."""
        # Create user, course, and note
        user = await register_user(
            db_session,
            email="test@example.com",
            password="password123",
            full_name="Test User"
        )
        course = await create_course(
            db_session,
            user_id=user.id,
            name="CS 101",
            color="#3B82F6"
        )
        note = await create_note(
            db_session,
            course_id=course.id,
            title="Test Note",
            content="Test content"
        )
        
        # Delete note
        await delete_note(
            db=db_session,
            note_id=note.id
        )
        
        # Verify note is deleted
        from sqlalchemy.future import select
        result = await db_session.execute(
            select(Note).where(Note.id == note.id)
        )
        deleted_note = result.scalar_one_or_none()
        
        assert deleted_note is None
    
    async def test_link_note_to_task(self, db_session: AsyncSession):
        """T194 [RED]: Test linking a note to a task."""
        from src.study_helper.services.note import link_note_to_task
        
        # Create user, course, note, and task
        user = await register_user(
            db_session,
            email="test@example.com",
            password="password123",
            full_name="Test User"
        )
        course = await create_course(
            db_session,
            user_id=user.id,
            name="CS 101",
            color="#3B82F6"
        )
        note = await create_note(
            db_session,
            course_id=course.id,
            title="Lecture Notes",
            content="Content"
        )
        task = await create_task(
            db_session,
            course_id=course.id,
            title="Assignment 1",
            priority="high"
        )
        
        # Link note to task
        link = await link_note_to_task(
            db=db_session,
            note_id=note.id,
            task_id=task.id
        )
        
        assert link is not None
        assert link.note_id == note.id
        assert link.task_id == task.id
    
    async def test_link_note_to_task_duplicate_fails(self, db_session: AsyncSession):
        """T195 [RED]: Test duplicate link raises error."""
        from src.study_helper.services.note import link_note_to_task
        from sqlalchemy.exc import IntegrityError
        
        # Create user, course, note, and task
        user = await register_user(
            db_session,
            email="test@example.com",
            password="password123",
            full_name="Test User"
        )
        course = await create_course(
            db_session,
            user_id=user.id,
            name="CS 101",
            color="#3B82F6"
        )
        note = await create_note(
            db_session,
            course_id=course.id,
            title="Notes",
            content="Content"
        )
        task = await create_task(
            db_session,
            course_id=course.id,
            title="Task",
            priority="medium"
        )
        
        # Create first link
        await link_note_to_task(db_session, note.id, task.id)
        
        # Attempt duplicate link - should fail
        with pytest.raises(IntegrityError):
            await link_note_to_task(db_session, note.id, task.id)
    
    async def test_unlink_note_from_task(self, db_session: AsyncSession):
        """T196 [RED]: Test unlinking a note from a task."""
        from src.study_helper.services.note import link_note_to_task, unlink_note_from_task
        from src.study_helper.models.note_task_link import NoteTaskLink
        from sqlalchemy.future import select
        
        # Create user, course, note, and task
        user = await register_user(
            db_session,
            email="test@example.com",
            password="password123",
            full_name="Test User"
        )
        course = await create_course(
            db_session,
            user_id=user.id,
            name="CS 101",
            color="#3B82F6"
        )
        note = await create_note(
            db_session,
            course_id=course.id,
            title="Notes",
            content="Content"
        )
        task = await create_task(
            db_session,
            course_id=course.id,
            title="Task",
            priority="low"
        )
        
        # Create link
        await link_note_to_task(db_session, note.id, task.id)
        
        # Verify link exists
        result = await db_session.execute(
            select(NoteTaskLink).where(
                NoteTaskLink.note_id == note.id,
                NoteTaskLink.task_id == task.id
            )
        )
        assert result.scalar_one_or_none() is not None
        
        # Unlink
        await unlink_note_from_task(
            db=db_session,
            note_id=note.id,
            task_id=task.id
        )
        
        # Verify link is removed
        result = await db_session.execute(
            select(NoteTaskLink).where(
                NoteTaskLink.note_id == note.id,
                NoteTaskLink.task_id == task.id
            )
        )
        assert result.scalar_one_or_none() is None
    
    async def test_delete_note_removes_links_keeps_tasks(self, db_session: AsyncSession):
        """T197 [RED]: Test deleting a note removes links but keeps tasks."""
        from src.study_helper.services.note import link_note_to_task
        from src.study_helper.models.note_task_link import NoteTaskLink
        from src.study_helper.models.task import Task
        from sqlalchemy.future import select
        
        # Create user, course, note, and task
        user = await register_user(
            db_session,
            email="test@example.com",
            password="password123",
            full_name="Test User"
        )
        course = await create_course(
            db_session,
            user_id=user.id,
            name="CS 101",
            color="#3B82F6"
        )
        note = await create_note(
            db_session,
            course_id=course.id,
            title="Notes",
            content="Content"
        )
        task = await create_task(
            db_session,
            course_id=course.id,
            title="Task",
            priority="high"
        )
        
        # Link note to task
        await link_note_to_task(db_session, note.id, task.id)
        
        # Delete note
        await delete_note(db_session, note.id)
        
        # Verify note is deleted
        result = await db_session.execute(
            select(Note).where(Note.id == note.id)
        )
        assert result.scalar_one_or_none() is None
        
        # Verify link is deleted (cascade)
        result = await db_session.execute(
            select(NoteTaskLink).where(NoteTaskLink.note_id == note.id)
        )
        assert result.scalar_one_or_none() is None
        
        # Verify task still exists
        result = await db_session.execute(
            select(Task).where(Task.id == task.id)
        )
        assert result.scalar_one_or_none() is not None

