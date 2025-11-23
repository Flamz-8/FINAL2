/**
 * Authentication API functions
 * T150: Auth endpoints (register, login)
 */

import apiClient from './client.js';

/**
 * Register a new user
 * @param {string} email - User email
 * @param {string} password - User password
 * @param {string} full_name - User's full name
 * @returns {Promise<{id: number, email: string, full_name: string, is_active: boolean, created_at: string}>}
 */
export async function register(email, password, full_name) {
    const data = await apiClient.post('/api/v1/auth/register', {
        email,
        password,
        full_name,
    });
    return data;
}

/**
 * Login user and get JWT token
 * @param {string} email - User email
 * @param {string} password - User password
 * @returns {Promise<{access_token: string, token_type: string}>}
 */
export async function login(email, password) {
    // FastAPI OAuth2 expects form data, not JSON
    const formData = new URLSearchParams();
    formData.append('username', email); // OAuth2 spec uses 'username' field
    formData.append('password', password);

    const response = await fetch(`${apiClient.baseURL}/api/v1/auth/login`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: formData,
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Login failed');
    }

    const data = await response.json();
    
    // Store token in localStorage
    apiClient.setToken(data.access_token);
    
    return data;
}

/**
 * Logout user (clear local token)
 */
export function logout() {
    apiClient.clearToken();
    window.location.reload();
}

/**
 * Get current user info
 * @returns {Promise<{id: number, email: string, full_name: string, is_active: boolean, created_at: string}>}
 */
export async function getCurrentUser() {
    return apiClient.get('/api/v1/auth/me');
}

/**
 * Check if user is authenticated
 */
export function isAuthenticated() {
    return !!apiClient.getToken();
}
