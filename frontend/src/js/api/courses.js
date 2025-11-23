/**
 * Course API functions
 * T151: Course CRUD operations
 */

import apiClient from './client.js';

/**
 * Create a new course
 * @param {string} title - Course title
 * @param {string} description - Course description (optional)
 * @param {string} color - Hex color code (e.g., "#FF5733")
 * @returns {Promise<Course>}
 */
export async function createCourse(title, description = '', color = '#3B82F6') {
    return apiClient.post('/api/v1/courses', {
        title,
        description,
        color,
    });
}

/**
 * Get all courses for current user
 * @param {boolean} archived - Include archived courses
 * @returns {Promise<Course[]>}
 */
export async function getCourses(archived = false) {
    return apiClient.get('/api/v1/courses', { archived });
}

/**
 * Get a single course by ID
 * @param {number} courseId - Course ID
 * @returns {Promise<Course>}
 */
export async function getCourse(courseId) {
    return apiClient.get(`/api/v1/courses/${courseId}`);
}

/**
 * Update a course
 * @param {number} courseId - Course ID
 * @param {Object} updates - Fields to update (title, description, color, is_archived)
 * @returns {Promise<Course>}
 */
export async function updateCourse(courseId, updates) {
    return apiClient.patch(`/api/v1/courses/${courseId}`, updates);
}

/**
 * Archive a course
 * @param {number} courseId - Course ID
 * @returns {Promise<Course>}
 */
export async function archiveCourse(courseId) {
    return updateCourse(courseId, { is_archived: true });
}

/**
 * Unarchive a course
 * @param {number} courseId - Course ID
 * @returns {Promise<Course>}
 */
export async function unarchiveCourse(courseId) {
    return updateCourse(courseId, { is_archived: false });
}

/**
 * Delete a course
 * @param {number} courseId - Course ID
 * @returns {Promise<void>}
 */
export async function deleteCourse(courseId) {
    return apiClient.delete(`/api/v1/courses/${courseId}`);
}
