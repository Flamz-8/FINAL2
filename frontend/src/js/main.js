/**
 * Main Application Entry Point
 * T157: App initialization, authentication, routing
 */

import { isAuthenticated, login, register, logout, getCurrentUser } from './api/auth.js';
import apiClient from './api/client.js';
import { showToast, showModal, hideModal, showLoading, hideLoading } from './utils/ui.js';
import { setupOfflineSync } from './utils/offline-queue.js';
import * as courseList from './components/course-list.js';
import * as noteEditor from './components/note-editor.js';
import * as taskList from './components/task-list.js';
import * as taskViews from './components/task-views.js';

/**
 * Initialize the application
 */
async function init() {
    // Check authentication
    if (!isAuthenticated()) {
        showAuthModal();
        return;
    }

    try {
        showLoading();
        
        // Setup offline sync
        setupOfflineSync(apiClient);
        
        // Get current user
        const user = await getCurrentUser();
        displayUser(user);
        
        // Initialize components
        courseList.init(onCourseSelect);
        noteEditor.init();
        taskList.init();
        taskViews.init(); // Initialize unified task views (US2)
        
        // Setup logout
        document.getElementById('logout-btn').addEventListener('click', handleLogout);
        
        // Hide auth modal, show app
        hideModal('auth-modal');
        document.getElementById('app-container').classList.remove('hidden');
        
        hideLoading();
    } catch (error) {
        console.error('Initialization error:', error);
        showToast('Failed to initialize app. Please refresh.', 'error');
        logout();
    }
}

/**
 * Show authentication modal
 */
function showAuthModal() {
    const modal = document.getElementById('auth-modal');
    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');
    const showRegisterBtn = document.getElementById('show-register');
    const showLoginBtn = document.getElementById('show-login');

    // Toggle between login and register
    showRegisterBtn.addEventListener('click', (e) => {
        e.preventDefault();
        loginForm.classList.add('hidden');
        registerForm.classList.remove('hidden');
    });

    showLoginBtn.addEventListener('click', (e) => {
        e.preventDefault();
        registerForm.classList.add('hidden');
        loginForm.classList.remove('hidden');
    });

    // Login form submission
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new FormData(e.target);
        const email = formData.get('email');
        const password = formData.get('password');

        try {
            showLoading();
            await login(email, password);
            showToast('Login successful!', 'success');
            window.location.reload(); // Reload to initialize app
        } catch (error) {
            showToast(error.message, 'error');
        } finally {
            hideLoading();
        }
    });

    // Register form submission
    registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new FormData(e.target);
        const email = formData.get('email');
        const password = formData.get('password');
        const fullName = formData.get('full_name');

        try {
            showLoading();
            await register(email, password, fullName);
            showToast('Registration successful! Please login.', 'success');
            
            // Switch to login form
            registerForm.classList.add('hidden');
            loginForm.classList.remove('hidden');
        } catch (error) {
            showToast(error.message, 'error');
        } finally {
            hideLoading();
        }
    });

    showModal('auth-modal');
}

/**
 * Display user information
 */
function displayUser(user) {
    const userNameEl = document.getElementById('user-name');
    if (userNameEl) {
        userNameEl.textContent = user.full_name || user.email;
    }
}

/**
 * Handle course selection
 */
function onCourseSelect(course) {
    // Hide welcome message, show course content
    document.getElementById('welcome-message').classList.add('hidden');
    document.getElementById('course-content').classList.remove('hidden');

    // Update course header
    document.getElementById('course-title').textContent = course.title;
    document.getElementById('course-description').textContent = course.description || 'No description';

    // Load notes and tasks for selected course
    noteEditor.loadNotes(course.id);
    taskList.loadTasks(course.id);
}

/**
 * Handle logout
 */
function handleLogout() {
    if (confirm('Are you sure you want to logout?')) {
        logout();
    }
}

// Start the application when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
