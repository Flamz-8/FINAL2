/**
 * Task List Component
 * T156: Task management UI
 */

import { createTask, getTasksByCourse, toggleTaskCompletion, updateTask, deleteTask } from '../api/tasks.js';
import { showToast, showLoading, hideLoading } from '../utils/ui.js';

let currentCourseId = null;
let tasks = [];

/**
 * Initialize task list component
 */
export function init() {
    document.getElementById('add-task-btn').addEventListener('click', handleAddTask);
}

/**
 * Load tasks for a course
 */
export async function loadTasks(courseId) {
    currentCourseId = courseId;
    
    try {
        showLoading();
        tasks = await getTasksByCourse(courseId, null, 'due_date', 'asc');
        renderTasks();
    } catch (error) {
        showToast(`Failed to load tasks: ${error.message}`, 'error');
    } finally {
        hideLoading();
    }
}

/**
 * Render tasks list
 */
function renderTasks() {
    const container = document.getElementById('tasks-list');
    
    if (tasks.length === 0) {
        container.innerHTML = `
            <div class="text-gray-500 text-sm text-center py-8">
                No tasks yet. Click "Add Task" to create one!
            </div>
        `;
        return;
    }

    container.innerHTML = tasks.map(task => `
        <div class="task-item ${task.is_completed ? 'completed' : ''}" data-task-id="${task.id}">
            <input type="checkbox" 
                   class="task-checkbox" 
                   ${task.is_completed ? 'checked' : ''}
                   data-task-id="${task.id}">
            
            <div class="task-content flex-1">
                <div class="task-title">${escapeHtml(task.title)}</div>
                ${task.description ? `<div class="task-description">${escapeHtml(task.description)}</div>` : ''}
                <div class="task-meta">
                    <span class="priority-badge priority-${task.priority}">${task.priority}</span>
                    ${task.due_date ? `<span class="task-due-date ${isOverdue(task.due_date) ? 'text-red-600 font-semibold' : ''}">${formatDueDate(task.due_date)}</span>` : ''}
                </div>
            </div>

            <div class="task-actions">
                <button class="text-blue-500 hover:text-blue-700 text-sm" 
                        data-action="edit"
                        title="Edit">
                    ✏️
                </button>
                <button class="text-red-500 hover:text-red-700 text-sm" 
                        data-action="delete"
                        title="Delete">
                    🗑️
                </button>
            </div>
        </div>
    `).join('');

    // Add click handlers
    container.querySelectorAll('.task-checkbox').forEach(checkbox => {
        checkbox.addEventListener('change', async (e) => {
            const taskId = parseInt(e.target.dataset.taskId);
            await handleToggleComplete(taskId, e.target.checked);
        });
    });

    container.querySelectorAll('[data-action]').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            const taskId = parseInt(btn.closest('.task-item').dataset.taskId);
            const action = btn.dataset.action;
            handleTaskAction(action, taskId);
        });
    });
}

/**
 * Handle add task button
 */
async function handleAddTask() {
    if (!currentCourseId) {
        showToast('Please select a course first', 'warning');
        return;
    }

    const title = prompt('Task title:');
    if (!title) return;

    const description = prompt('Description (optional):') || '';
    const dueDateStr = prompt('Due date (YYYY-MM-DD, optional):') || null;
    const priority = prompt('Priority (low/medium/high):', 'medium') || 'medium';

    // Validate priority
    if (!['low', 'medium', 'high'].includes(priority)) {
        showToast('Invalid priority. Must be low, medium, or high.', 'error');
        return;
    }

    try {
        showLoading();
        const newTask = await createTask(currentCourseId, title, dueDateStr, priority, description);
        tasks.push(newTask);
        renderTasks();
        showToast('Task created!', 'success');
    } catch (error) {
        showToast(`Failed to create task: ${error.message}`, 'error');
    } finally {
        hideLoading();
    }
}

/**
 * Handle toggle task completion
 */
async function handleToggleComplete(taskId, completed) {
    try {
        await toggleTaskCompletion(taskId, completed);
        const task = tasks.find(t => t.id === taskId);
        if (task) {
            task.is_completed = completed;
            renderTasks();
        }
    } catch (error) {
        showToast(`Failed to update task: ${error.message}`, 'error');
        // Revert checkbox
        const checkbox = document.querySelector(`input[data-task-id="${taskId}"]`);
        if (checkbox) checkbox.checked = !completed;
    }
}

/**
 * Handle task actions (edit, delete)
 */
async function handleTaskAction(action, taskId) {
    const task = tasks.find(t => t.id === taskId);
    if (!task) return;

    try {
        showLoading();

        switch (action) {
            case 'edit':
                const newTitle = prompt('Task title:', task.title);
                if (!newTitle) return;
                
                const newDescription = prompt('Description:', task.description) || '';
                const newDueDateStr = prompt('Due date (YYYY-MM-DD):', task.due_date || '') || null;
                const newPriority = prompt('Priority (low/medium/high):', task.priority) || 'medium';
                
                if (!['low', 'medium', 'high'].includes(newPriority)) {
                    showToast('Invalid priority', 'error');
                    return;
                }
                
                await updateTask(taskId, { 
                    title: newTitle, 
                    description: newDescription,
                    due_date: newDueDateStr,
                    priority: newPriority
                });
                
                Object.assign(task, { 
                    title: newTitle, 
                    description: newDescription,
                    due_date: newDueDateStr,
                    priority: newPriority
                });
                renderTasks();
                showToast('Task updated!', 'success');
                break;

            case 'delete':
                if (!confirm(`Delete task "${task.title}"?`)) return;
                await deleteTask(taskId);
                tasks = tasks.filter(t => t.id !== taskId);
                renderTasks();
                showToast('Task deleted!', 'success');
                break;
        }
    } catch (error) {
        showToast(`Failed to ${action} task: ${error.message}`, 'error');
    } finally {
        hideLoading();
    }
}

/**
 * Check if task is overdue
 */
function isOverdue(dueDateStr) {
    if (!dueDateStr) return false;
    const dueDate = new Date(dueDateStr);
    const now = new Date();
    now.setHours(0, 0, 0, 0); // Compare dates only, not times
    return dueDate < now;
}

/**
 * Format due date for display
 */
function formatDueDate(dueDateStr) {
    const dueDate = new Date(dueDateStr);
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);

    const dueDay = new Date(dueDate.getFullYear(), dueDate.getMonth(), dueDate.getDate());

    if (dueDay.getTime() === today.getTime()) {
        return 'Due today';
    } else if (dueDay.getTime() === tomorrow.getTime()) {
        return 'Due tomorrow';
    } else if (dueDay < today) {
        const diffDays = Math.floor((today - dueDay) / 86400000);
        return `Overdue by ${diffDays}d`;
    } else {
        return `Due ${dueDate.toLocaleDateString()}`;
    }
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
