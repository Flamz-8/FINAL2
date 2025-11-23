/**
 * Note API functions
 * T152: Note CRUD operations
 */

import apiClient from './client.js';

/**
 * Create a new note
 * @param {number} courseId - Course ID
 * @param {string} title - Note title
 * @param {string} content - Note content (markdown)
 * @returns {Promise<Note>}
 */
export async function createNote(courseId, title, content = '') {
    return apiClient.post('/api/v1/notes', {
        course_id: courseId,
        title,
        content,
    });
}

/**
 * Get all notes for a course
 * @param {number} courseId - Course ID
 * @returns {Promise<Note[]>}
 */
export async function getNotesByCourse(courseId) {
    return apiClient.get(`/api/v1/courses/${courseId}/notes`);
}

/**
 * Get a single note by ID
 * @param {number} noteId - Note ID
 * @returns {Promise<Note>}
 */
export async function getNote(noteId) {
    return apiClient.get(`/api/v1/notes/${noteId}`);
}

/**
 * Update a note
 * @param {number} noteId - Note ID
 * @param {Object} updates - Fields to update (title, content)
 * @returns {Promise<Note>}
 */
export async function updateNote(noteId, updates) {
    return apiClient.patch(`/api/v1/notes/${noteId}`, updates);
}

/**
 * Delete a note
 * @param {number} noteId - Note ID
 * @returns {Promise<void>}
 */
export async function deleteNote(noteId) {
    return apiClient.delete(`/api/v1/notes/${noteId}`);
}
