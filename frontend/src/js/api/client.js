/**
 * Base HTTP client with JWT token injection
 * T149: API client with authentication
 */

import { enqueue } from '../utils/offline-queue.js';

const API_BASE_URL = 'http://localhost:8000';

class APIClient {
    constructor(baseURL = API_BASE_URL) {
        this.baseURL = baseURL;
    }

    /**
     * Get JWT token from localStorage
     */
    getToken() {
        return localStorage.getItem('token');
    }

    /**
     * Set JWT token in localStorage
     */
    setToken(token) {
        localStorage.setItem('token', token);
    }

    /**
     * Remove JWT token from localStorage
     */
    clearToken() {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
    }

    /**
     * Get default headers with JWT token
     */
    getHeaders() {
        const headers = {
            'Content-Type': 'application/json',
        };

        const token = this.getToken();
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        return headers;
    }

    /**
     * Make HTTP request
     */
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            ...options,
            headers: {
                ...this.getHeaders(),
                ...options.headers,
            },
        };

        try {
            const response = await fetch(url, config);
            
            // Handle 401 Unauthorized - token expired or invalid
            if (response.status === 401) {
                this.clearToken();
                window.location.reload();
                throw new Error('Session expired. Please login again.');
            }

            // Parse JSON response
            let data = null;
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                data = await response.json();
            }

            // Handle non-2xx responses
            if (!response.ok) {
                const error = new Error(data?.detail || `HTTP ${response.status}: ${response.statusText}`);
                error.status = response.status;
                error.data = data;
                throw error;
            }

            return data;
        } catch (error) {
            // Network errors or other fetch failures
            if (error.name === 'TypeError' || !navigator.onLine) {
                // Queue request for retry if it's a mutation (POST, PATCH, DELETE)
                if (['POST', 'PATCH', 'DELETE'].includes(config.method)) {
                    enqueue(config.method, endpoint, JSON.parse(config.body || '{}'));
                }
                throw new Error('Network error. Request queued for retry when online.');
            }
            throw error;
        }
    }

    /**
     * GET request
     */
    async get(endpoint, params = {}) {
        const queryString = new URLSearchParams(params).toString();
        const url = queryString ? `${endpoint}?${queryString}` : endpoint;
        return this.request(url, { method: 'GET' });
    }

    /**
     * POST request
     */
    async post(endpoint, data = {}) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data),
        });
    }

    /**
     * PATCH request
     */
    async patch(endpoint, data = {}) {
        return this.request(endpoint, {
            method: 'PATCH',
            body: JSON.stringify(data),
        });
    }

    /**
     * DELETE request
     */
    async delete(endpoint) {
        return this.request(endpoint, { method: 'DELETE' });
    }
}

// Create singleton instance
const apiClient = new APIClient();

export default apiClient;
