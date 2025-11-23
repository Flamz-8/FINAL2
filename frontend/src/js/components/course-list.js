/**
 * Course List Component
 * T154: Render and manage course list UI
 */

import { getCourses, createCourse, updateCourse, deleteCourse, archiveCourse } from '../api/courses.js';
import { showToast, showLoading, hideLoading } from '../utils/ui.js';

let courses = [];
let selectedCourseId = null;

/**
 * Initialize course list component
 */
export function init(onCourseSelect) {
    document.getElementById('add-course-btn').addEventListener('click', handleAddCourse);
    loadCourses(onCourseSelect);
}

/**
 * Load courses from API
 */
async function loadCourses(onCourseSelect) {
    try {
        showLoading();
        courses = await getCourses(false); // Don't include archived
        renderCourses(onCourseSelect);
    } catch (error) {
        showToast(`Failed to load courses: ${error.message}`, 'error');
    } finally {
        hideLoading();
    }
}

/**
 * Render course list in sidebar
 */
function renderCourses(onCourseSelect) {
    const container = document.getElementById('course-list');
    
    if (courses.length === 0) {
        container.innerHTML = `
            <div class="text-gray-500 text-sm text-center py-4">
                No courses yet.<br>Click "+" to add one!
            </div>
        `;
        return;
    }

    container.innerHTML = courses.map(course => `
        <div class="course-item ${selectedCourseId === course.id ? 'active' : ''}" 
             data-course-id="${course.id}"
             style="border-left: 4px solid ${course.color}">
            <div class="flex-1">
                <div class="font-semibold">${escapeHtml(course.title)}</div>
                ${course.description ? `<div class="text-sm text-gray-600 truncate">${escapeHtml(course.description)}</div>` : ''}
            </div>
            <div class="course-actions" style="display: none;">
                <button class="text-blue-500 hover:text-blue-700" 
                        data-action="edit" 
                        title="Edit">
                    ✏️
                </button>
                <button class="text-yellow-500 hover:text-yellow-700" 
                        data-action="archive" 
                        title="Archive">
                    📦
                </button>
                <button class="text-red-500 hover:text-red-700" 
                        data-action="delete" 
                        title="Delete">
                    🗑️
                </button>
            </div>
        </div>
    `).join('');

    // Add click handlers
    container.querySelectorAll('.course-item').forEach(item => {
        const courseId = parseInt(item.dataset.courseId);
        
        // Show actions on hover
        item.addEventListener('mouseenter', () => {
            item.querySelector('.course-actions').style.display = 'flex';
        });
        item.addEventListener('mouseleave', () => {
            item.querySelector('.course-actions').style.display = 'none';
        });

        // Course selection
        item.addEventListener('click', (e) => {
            if (!e.target.closest('.course-actions')) {
                selectCourse(courseId, onCourseSelect);
            }
        });

        // Action buttons
        item.querySelectorAll('[data-action]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const action = btn.dataset.action;
                handleCourseAction(action, courseId, onCourseSelect);
            });
        });
    });
}

/**
 * Select a course
 */
function selectCourse(courseId, onCourseSelect) {
    selectedCourseId = courseId;
    const course = courses.find(c => c.id === courseId);
    
    // Update UI
    document.querySelectorAll('.course-item').forEach(item => {
        item.classList.toggle('active', parseInt(item.dataset.courseId) === courseId);
    });

    // Notify parent
    if (onCourseSelect && course) {
        onCourseSelect(course);
    }
}

/**
 * Handle add course button
 */
async function handleAddCourse() {
    const title = prompt('Course name:');
    if (!title) return;

    const description = prompt('Description (optional):') || '';
    const color = prompt('Color (hex code, e.g., #3B82F6):') || '#3B82F6';

    try {
        showLoading();
        const newCourse = await createCourse(title, description, color);
        courses.push(newCourse);
        renderCourses();
        showToast('Course created successfully!', 'success');
    } catch (error) {
        showToast(`Failed to create course: ${error.message}`, 'error');
    } finally {
        hideLoading();
    }
}

/**
 * Handle course actions (edit, archive, delete)
 */
async function handleCourseAction(action, courseId, onCourseSelect) {
    const course = courses.find(c => c.id === courseId);
    if (!course) return;

    try {
        showLoading();

        switch (action) {
            case 'edit':
                const newTitle = prompt('Course name:', course.title);
                if (!newTitle) return;
                
                const newDescription = prompt('Description:', course.description) || '';
                const newColor = prompt('Color (hex):', course.color) || course.color;
                
                await updateCourse(courseId, { 
                    title: newTitle, 
                    description: newDescription,
                    color: newColor 
                });
                
                Object.assign(course, { title: newTitle, description: newDescription, color: newColor });
                renderCourses(onCourseSelect);
                showToast('Course updated!', 'success');
                break;

            case 'archive':
                if (!confirm(`Archive "${course.title}"?`)) return;
                await archiveCourse(courseId);
                courses = courses.filter(c => c.id !== courseId);
                
                if (selectedCourseId === courseId) {
                    selectedCourseId = null;
                    document.getElementById('welcome-message').classList.remove('hidden');
                    document.getElementById('course-content').classList.add('hidden');
                }
                
                renderCourses(onCourseSelect);
                showToast('Course archived!', 'success');
                break;

            case 'delete':
                if (!confirm(`Delete "${course.title}"? This will delete all notes and tasks!`)) return;
                await deleteCourse(courseId);
                courses = courses.filter(c => c.id !== courseId);
                
                if (selectedCourseId === courseId) {
                    selectedCourseId = null;
                    document.getElementById('welcome-message').classList.remove('hidden');
                    document.getElementById('course-content').classList.add('hidden');
                }
                
                renderCourses(onCourseSelect);
                showToast('Course deleted!', 'success');
                break;
        }
    } catch (error) {
        showToast(`Failed to ${action} course: ${error.message}`, 'error');
    } finally {
        hideLoading();
    }
}

/**
 * Get currently selected course
 */
export function getSelectedCourse() {
    return courses.find(c => c.id === selectedCourseId);
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
