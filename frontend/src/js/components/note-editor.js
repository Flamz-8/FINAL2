/**
 * Note Editor Component
 * T155: Markdown editor for notes
 */

import { createNote, getNotesByCourse, updateNote, deleteNote } from '../api/notes.js';
import { showToast, showLoading, hideLoading } from '../utils/ui.js';

let currentCourseId = null;
let notes = [];

/**
 * Initialize note editor component
 */
export function init() {
    document.getElementById('add-note-btn').addEventListener('click', handleAddNote);
}

/**
 * Load notes for a course
 */
export async function loadNotes(courseId) {
    currentCourseId = courseId;
    
    try {
        showLoading();
        notes = await getNotesByCourse(courseId);
        renderNotes();
    } catch (error) {
        showToast(`Failed to load notes: ${error.message}`, 'error');
    } finally {
        hideLoading();
    }
}

/**
 * Render notes list
 */
function renderNotes() {
    const container = document.getElementById('notes-list');
    
    if (notes.length === 0) {
        container.innerHTML = `
            <div class="text-gray-500 text-sm text-center py-8">
                No notes yet. Click "Add Note" to create one!
            </div>
        `;
        return;
    }

    container.innerHTML = notes.map(note => `
        <div class="note-card" data-note-id="${note.id}">
            <div class="flex justify-between items-start mb-2">
                <h3 class="font-semibold text-lg">${escapeHtml(note.title)}</h3>
                <div class="note-actions">
                    <button class="text-blue-500 hover:text-blue-700 text-sm" 
                            data-action="edit"
                            title="Edit">
                        ✏️
                    </button>
                    <button class="text-red-500 hover:text-red-700 text-sm" 
                            data-action="delete"
                            title="Delete">
                        🗑️
                    </button>
                </div>
            </div>
            <div class="note-preview markdown-content">
                ${renderMarkdown(note.content)}
            </div>
            <div class="text-xs text-gray-500 mt-2">
                Updated ${formatDate(note.updated_at)}
            </div>
        </div>
    `).join('');

    // Add click handlers
    container.querySelectorAll('.note-card').forEach(card => {
        const noteId = parseInt(card.dataset.noteId);
        
        card.querySelectorAll('[data-action]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const action = btn.dataset.action;
                handleNoteAction(action, noteId);
            });
        });

        // Expand note on click
        card.addEventListener('click', () => {
            const preview = card.querySelector('.note-preview');
            preview.classList.toggle('expanded');
        });
    });
}

/**
 * Handle add note button
 */
async function handleAddNote() {
    if (!currentCourseId) {
        showToast('Please select a course first', 'warning');
        return;
    }

    const title = prompt('Note title:');
    if (!title) return;

    const content = prompt('Note content (markdown):') || '';

    try {
        showLoading();
        const newNote = await createNote(currentCourseId, title, content);
        notes.push(newNote);
        renderNotes();
        showToast('Note created!', 'success');
    } catch (error) {
        showToast(`Failed to create note: ${error.message}`, 'error');
    } finally {
        hideLoading();
    }
}

/**
 * Handle note actions (edit, delete)
 */
async function handleNoteAction(action, noteId) {
    const note = notes.find(n => n.id === noteId);
    if (!note) return;

    try {
        showLoading();

        switch (action) {
            case 'edit':
                const newTitle = prompt('Note title:', note.title);
                if (!newTitle) return;
                
                const newContent = prompt('Note content (markdown):', note.content) || '';
                
                await updateNote(noteId, { title: newTitle, content: newContent });
                Object.assign(note, { title: newTitle, content: newContent });
                renderNotes();
                showToast('Note updated!', 'success');
                break;

            case 'delete':
                if (!confirm(`Delete note "${note.title}"?`)) return;
                await deleteNote(noteId);
                notes = notes.filter(n => n.id !== noteId);
                renderNotes();
                showToast('Note deleted!', 'success');
                break;
        }
    } catch (error) {
        showToast(`Failed to ${action} note: ${error.message}`, 'error');
    } finally {
        hideLoading();
    }
}

/**
 * Simple markdown renderer
 */
function renderMarkdown(text) {
    if (!text) return '<em class="text-gray-400">No content</em>';
    
    // Truncate for preview
    const maxLength = 200;
    let preview = text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
    
    // Basic markdown rendering
    preview = escapeHtml(preview)
        .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>') // Bold
        .replace(/\*(.+?)\*/g, '<em>$1</em>') // Italic
        .replace(/`(.+?)`/g, '<code>$1</code>') // Inline code
        .replace(/^### (.+)$/gm, '<h3>$1</h3>') // H3
        .replace(/^## (.+)$/gm, '<h2>$1</h2>') // H2
        .replace(/^# (.+)$/gm, '<h1>$1</h1>') // H1
        .replace(/\n/g, '<br>'); // Line breaks
    
    return preview;
}

/**
 * Format date for display
 */
function formatDate(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    
    return date.toLocaleDateString();
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
