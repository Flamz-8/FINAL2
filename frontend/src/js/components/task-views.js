/**
 * Task Views Component - Today/Week/Upcoming Tabs
 * T182-T187: Unified task view across all courses
 */

import { showToast, showLoading, hideLoading } from '../utils/ui.js';

/**
 * Initialize task views component
 */
export async function init() {
    const container = document.getElementById('task-views-container');
    if (!container) {
        console.warn('Task views container not found');
        return;
    }

    // Render tabs
    container.innerHTML = `
        <div class="task-views">
            <div class="task-tabs">
                <button class="task-tab active" data-view="today">
                    📅 Today
                    <span class="task-count" id="today-count">0</span>
                </button>
                <button class="task-tab" data-view="week">
                    📆 This Week
                    <span class="task-count" id="week-count">0</span>
                </button>
                <button class="task-tab" data-view="upcoming">
                    🗓️ Upcoming
                    <span class="task-count" id="upcoming-count">0</span>
                </button>
            </div>
            <div class="task-view-content">
                <div id="view-today" class="view-panel active"></div>
                <div id="view-week" class="view-panel hidden"></div>
                <div id="view-upcoming" class="view-panel hidden"></div>
            </div>
        </div>
    `;

    // Setup tab switching (T183)
    setupTabSwitching();

    // Load initial view
    await loadView('today');
}

/**
 * Setup tab switching with active state (T183)
 */
function setupTabSwitching() {
    const tabs = document.querySelectorAll('.task-tab');
    
    tabs.forEach(tab => {
        tab.addEventListener('click', async () => {
            const view = tab.dataset.view;
            
            // Performance tracking (T187)
            const startTime = performance.now();
            
            // Update active states
            tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            
            document.querySelectorAll('.view-panel').forEach(panel => {
                panel.classList.add('hidden');
                panel.classList.remove('active');
            });
            
            const panel = document.getElementById(`view-${view}`);
            panel.classList.remove('hidden');
            panel.classList.add('active');
            
            // Load view data
            await loadView(view);
            
            // Check performance (T187)
            const elapsed = performance.now() - startTime;
            if (elapsed > 100) {
                console.warn(`Tab switch took ${elapsed.toFixed(2)}ms (target: <100ms)`);
            }
        });
    });
}

/**
 * Load tasks for specific view
 */
async function loadView(view) {
    try {
        showLoading();
        
        const response = await fetch(`http://localhost:8000/api/v1/tasks/${view}`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });
        
        if (!response.ok) throw new Error('Failed to load tasks');
        
        const tasks = await response.json();
        
        // Update count badge
        document.getElementById(`${view}-count`).textContent = tasks.length;
        
        // Render tasks
        renderTasks(view, tasks);
    } catch (error) {
        showToast(`Failed to load ${view} tasks: ${error.message}`, 'error');
    } finally {
        hideLoading();
    }
}

/**
 * Render tasks for a view (T184-T186)
 */
function renderTasks(view, tasks) {
    const panel = document.getElementById(`view-${view}`);
    
    if (tasks.length === 0) {
        panel.innerHTML = `
            <div class="empty-state">
                <p class="text-gray-500 text-center py-8">
                    No tasks ${view === 'today' ? 'due today' : view === 'week' ? 'this week' : 'upcoming'} 
                </p>
            </div>
        `;
        return;
    }
    
    // Group tasks by category and sort by priority (T186)
    const grouped = groupAndSortTasks(tasks);
    
    let html = '';
    
    // Render overdue tasks first (T184)
    if (grouped.overdue.length > 0) {
        html += `
            <div class="task-group overdue-group">
                <h3 class="task-group-title text-red-600 font-semibold">
                    ⚠️ Overdue (${grouped.overdue.length})
                </h3>
                ${renderTaskList(grouped.overdue, true)}
            </div>
        `;
    }
    
    // Render tasks by date
    for (const [date, taskList] of Object.entries(grouped.byDate)) {
        const isToday = new Date(date).toDateString() === new Date().toDateString();
        const dateLabel = isToday ? 'Today' : formatDate(date);
        
        html += `
            <div class="task-group">
                <h3 class="task-group-title ${isToday ? 'text-blue-600' : 'text-gray-700'} font-semibold">
                    ${dateLabel} (${taskList.length})
                </h3>
                ${renderTaskList(taskList, false)}
            </div>
        `;
    }
    
    // Render tasks without due date (T185)
    if (grouped.noDueDate.length > 0) {
        html += `
            <div class="task-group no-due-date-group">
                <h3 class="task-group-title text-gray-500 font-semibold">
                    📋 No Due Date (${grouped.noDueDate.length})
                </h3>
                ${renderTaskList(grouped.noDueDate, false)}
            </div>
        `;
    }
    
    panel.innerHTML = html;
    
    // Attach event listeners
    attachTaskListeners(panel);
}

/**
 * Group tasks by category and sort by priority (T186)
 */
function groupAndSortTasks(tasks) {
    const now = new Date();
    now.setHours(0, 0, 0, 0);
    
    const grouped = {
        overdue: [],
        byDate: {},
        noDueDate: []
    };
    
    // Priority order for sorting (T186)
    const priorityOrder = { high: 0, medium: 1, low: 2 };
    
    tasks.forEach(task => {
        if (!task.due_date) {
            grouped.noDueDate.push(task);
        } else {
            const dueDate = new Date(task.due_date);
            dueDate.setHours(0, 0, 0, 0);
            
            if (dueDate < now && !task.is_completed) {
                grouped.overdue.push(task);
            } else {
                const dateKey = dueDate.toISOString().split('T')[0];
                if (!grouped.byDate[dateKey]) {
                    grouped.byDate[dateKey] = [];
                }
                grouped.byDate[dateKey].push(task);
            }
        }
    });
    
    // Sort each group by priority (high → medium → low) (T186)
    grouped.overdue.sort((a, b) => priorityOrder[a.priority] - priorityOrder[b.priority]);
    grouped.noDueDate.sort((a, b) => priorityOrder[a.priority] - priorityOrder[b.priority]);
    
    for (const date in grouped.byDate) {
        grouped.byDate[date].sort((a, b) => priorityOrder[a.priority] - priorityOrder[b.priority]);
    }
    
    return grouped;
}

/**
 * Render a list of tasks
 */
function renderTaskList(tasks, isOverdue) {
    return tasks.map(task => `
        <div class="task-item ${task.is_completed ? 'completed' : ''} ${isOverdue ? 'overdue' : ''}" 
             data-task-id="${task.id}">
            <input type="checkbox" 
                   class="task-checkbox" 
                   ${task.is_completed ? 'checked' : ''}
                   data-task-id="${task.id}">
            
            <div class="task-content flex-1">
                <div class="task-title ${isOverdue ? 'text-red-600' : ''}">
                    ${isOverdue ? '⚠️ ' : ''}${escapeHtml(task.title)}
                </div>
                ${task.description ? `<div class="task-description">${escapeHtml(task.description)}</div>` : ''}
                <div class="task-meta">
                    <span class="priority-badge priority-${task.priority}">${task.priority}</span>
                    <span class="text-xs text-gray-500">Course #${task.course_id}</span>
                </div>
            </div>
        </div>
    `).join('');
}

/**
 * Attach event listeners to tasks
 */
function attachTaskListeners(panel) {
    panel.querySelectorAll('.task-checkbox').forEach(checkbox => {
        checkbox.addEventListener('change', async (e) => {
            const taskId = parseInt(e.target.dataset.taskId);
            const completed = e.target.checked;
            
            try {
                const response = await fetch(`http://localhost:8000/api/v1/tasks/${taskId}`, {
                    method: 'PATCH',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${localStorage.getItem('token')}`
                    },
                    body: JSON.stringify({ is_completed: completed })
                });
                
                if (!response.ok) throw new Error('Failed to update task');
                
                // Reload current view
                const activeTab = document.querySelector('.task-tab.active');
                const view = activeTab.dataset.view;
                await loadView(view);
                
                showToast(completed ? 'Task completed!' : 'Task marked incomplete', 'success');
            } catch (error) {
                showToast(`Failed to update task: ${error.message}`, 'error');
                e.target.checked = !completed; // Revert
            }
        });
    });
}

/**
 * Format date for display
 */
function formatDate(dateString) {
    const date = new Date(dateString);
    const today = new Date();
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);
    
    if (date.toDateString() === today.toDateString()) {
        return 'Today';
    } else if (date.toDateString() === tomorrow.toDateString()) {
        return 'Tomorrow';
    } else {
        return date.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });
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

/**
 * Refresh all views
 */
export async function refresh() {
    const activeTab = document.querySelector('.task-tab.active');
    if (activeTab) {
        await loadView(activeTab.dataset.view);
    }
}
