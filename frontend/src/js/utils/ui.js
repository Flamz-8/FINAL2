/**
 * UI Utility Functions
 * Toast notifications, loading indicators, etc.
 */

/**
 * Show toast notification
 */
export function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toast-container') || createToastContainer();
    
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    
    toastContainer.appendChild(toast);
    
    // Auto remove after 3 seconds
    setTimeout(() => {
        toast.style.animation = 'slideOutRight 0.3s ease-out';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

/**
 * Create toast container if it doesn't exist
 */
function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.style.cssText = `
        position: fixed;
        top: 1rem;
        right: 1rem;
        z-index: 9999;
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    `;
    document.body.appendChild(container);
    return container;
}

/**
 * Show loading indicator
 */
export function showLoading() {
    const loading = document.getElementById('loading-indicator');
    if (loading) {
        loading.classList.remove('hidden');
    }
}

/**
 * Hide loading indicator
 */
export function hideLoading() {
    const loading = document.getElementById('loading-indicator');
    if (loading) {
        loading.classList.add('hidden');
    }
}

/**
 * Show modal
 */
export function showModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('hidden');
    }
}

/**
 * Hide modal
 */
export function hideModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('hidden');
    }
}
