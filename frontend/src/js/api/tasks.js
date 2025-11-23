/**
 * Task API functions
 * T153: Task CRUD operations
 */

import apiClient from './client.js';

/**
 * Create a new task
 * @param {number} courseId - Course ID
 * @param {string} title - Task title
 * @param {string} due_date - Due date (ISO 8601 string, optional)
 * @param {string} priority - Priority level ('low', 'medium', 'high')
 * @param {string} description - Task description (optional)
 * @returns {Promise<Task>}
 */
export async function createTask(courseId, title, due_date = null, priority = 'medium', description = '') {
    const data = {
        course_id: courseId,
        title,
        priority,
    };

    if (description) data.description = description;
    if (due_date) data.due_date = due_date;

    return apiClient.post('/api/v1/tasks', data);
}

/**
 * Get all tasks for a course
 * @param {number} courseId - Course ID
 * @param {boolean|null} completed - Filter by completion status (null = all)
 * @param {string} sort_by - Sort field ('due_date' or 'priority')
 * @param {string} order - Sort order ('asc' or 'desc')
 * @returns {Promise<Task[]>}
 */
export async function getTasksByCourse(courseId, completed = null, sort_by = 'due_date', order = 'asc') {
    const params = { sort_by, order };
    if (completed !== null) {
        params.completed = completed;
    }
    return apiClient.get(`/api/v1/courses/${courseId}/tasks`, params);
}

/**
 * Get a single task by ID
 * @param {number} taskId - Task ID
 * @returns {Promise<Task>}
 */
export async function getTask(taskId) {
    return apiClient.get(`/api/v1/tasks/${taskId}`);
}

/**
 * Update a task
 * @param {number} taskId - Task ID
 * @param {Object} updates - Fields to update (title, description, due_date, priority, is_completed)
 * @returns {Promise<Task>}
 */
export async function updateTask(taskId, updates) {
    return apiClient.patch(`/api/v1/tasks/${taskId}`, updates);
}

/**
 * Toggle task completion
 * @param {number} taskId - Task ID
 * @param {boolean} completed - Completion status
 * @returns {Promise<Task>}
 */
export async function toggleTaskCompletion(taskId, completed) {
    return updateTask(taskId, { is_completed: completed });
}

/**
 * Delete a task
 * @param {number} taskId - Task ID
 * @returns {Promise<void>}
 */
export async function deleteTask(taskId) {
    return apiClient.delete(`/api/v1/tasks/${taskId}`);
}
