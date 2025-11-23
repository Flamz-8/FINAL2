/**
 * Offline Queue Manager
 * T158: LocalStorage queue for failed API requests
 */

const QUEUE_KEY = 'offline_queue';
const MAX_RETRIES = 3;

/**
 * Queue item structure:
 * {
 *   id: string,
 *   method: string,
 *   endpoint: string,
 *   data: object,
 *   retries: number,
 *   timestamp: number
 * }
 */

/**
 * Add request to offline queue
 */
export function enqueue(method, endpoint, data = null) {
    const queue = getQueue();
    const item = {
        id: generateId(),
        method,
        endpoint,
        data,
        retries: 0,
        timestamp: Date.now()
    };
    
    queue.push(item);
    saveQueue(queue);
    
    console.log(`[OfflineQueue] Enqueued ${method} ${endpoint}`);
    return item.id;
}

/**
 * Process queue (retry failed requests)
 */
export async function processQueue(apiClient) {
    const queue = getQueue();
    if (queue.length === 0) return;

    console.log(`[OfflineQueue] Processing ${queue.length} items...`);
    
    const failed = [];
    
    for (const item of queue) {
        try {
            // Attempt request
            await apiClient.request(item.endpoint, {
                method: item.method,
                body: item.data ? JSON.stringify(item.data) : undefined
            });
            
            console.log(`[OfflineQueue] ✓ Success: ${item.method} ${item.endpoint}`);
        } catch (error) {
            item.retries++;
            
            if (item.retries < MAX_RETRIES) {
                console.log(`[OfflineQueue] ✗ Retry ${item.retries}/${MAX_RETRIES}: ${item.method} ${item.endpoint}`);
                failed.push(item);
            } else {
                console.log(`[OfflineQueue] ✗ Max retries exceeded: ${item.method} ${item.endpoint}`);
            }
        }
    }
    
    // Update queue with failed items only
    saveQueue(failed);
    
    if (failed.length === 0) {
        console.log('[OfflineQueue] All items processed successfully!');
    }
}

/**
 * Get queue from localStorage
 */
function getQueue() {
    try {
        const data = localStorage.getItem(QUEUE_KEY);
        return data ? JSON.parse(data) : [];
    } catch (error) {
        console.error('[OfflineQueue] Failed to load queue:', error);
        return [];
    }
}

/**
 * Save queue to localStorage
 */
function saveQueue(queue) {
    try {
        localStorage.setItem(QUEUE_KEY, JSON.stringify(queue));
    } catch (error) {
        console.error('[OfflineQueue] Failed to save queue:', error);
    }
}

/**
 * Clear queue
 */
export function clearQueue() {
    localStorage.removeItem(QUEUE_KEY);
    console.log('[OfflineQueue] Queue cleared');
}

/**
 * Get queue size
 */
export function getQueueSize() {
    return getQueue().length;
}

/**
 * Generate unique ID
 */
function generateId() {
    return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}

/**
 * Setup online/offline event listeners
 */
export function setupOfflineSync(apiClient) {
    window.addEventListener('online', async () => {
        console.log('[OfflineQueue] Connection restored, processing queue...');
        await processQueue(apiClient);
    });

    window.addEventListener('offline', () => {
        console.log('[OfflineQueue] Connection lost, requests will be queued');
    });

    // Check if online and process queue on init
    if (navigator.onLine) {
        processQueue(apiClient);
    }
}
