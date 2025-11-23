# StudyHelper Frontend

Single-page application (SPA) for students to manage courses, notes, and tasks.

## Features

- **Authentication**: Register and login with email/password
- **Courses**: Create, edit, archive, and delete courses with custom colors
- **Notes**: Markdown-based notes organized by course
- **Tasks**: Tasks with priorities, due dates, and completion tracking
- **Offline Support**: Requests queued when offline, synced when online

## Tech Stack

- **HTML5**: Semantic structure
- **Tailwind CSS 2.2.19**: Utility-first CSS framework (CDN)
- **Vanilla JavaScript**: ES6 modules, no build tools
- **LocalStorage**: Token storage and offline queue

## File Structure

```
frontend/src/
├── index.html              # Main HTML file
├── css/
│   └── main.css           # Custom styles
└── js/
    ├── main.js            # App entry point
    ├── api/
    │   ├── client.js      # HTTP client with JWT
    │   ├── auth.js        # Authentication API
    │   ├── courses.js     # Course CRUD
    │   ├── notes.js       # Note CRUD
    │   └── tasks.js       # Task CRUD
    ├── components/
    │   ├── course-list.js # Course sidebar
    │   ├── note-editor.js # Note management
    │   └── task-list.js   # Task management
    └── utils/
        ├── ui.js          # Toast, loading, modals
        └── offline-queue.js # Offline sync
```

## Running the App

1. **Start the backend server**:
   ```bash
   cd backend
   uv run uvicorn src.study_helper.main:app --reload
   ```

2. **Serve the frontend**:
   ```bash
   cd frontend/src
   python -m http.server 3000
   ```

3. **Open in browser**:
   ```
   http://localhost:3000
   ```

## Usage

1. **Register**: Create an account with email, password, and full name
2. **Login**: Sign in with your credentials
3. **Add Course**: Click "+" in sidebar, enter course name, description, and color
4. **Select Course**: Click on a course to view its notes and tasks
5. **Add Note**: Click "Add Note", enter title and markdown content
6. **Add Task**: Click "Add Task", enter title, due date, priority
7. **Complete Task**: Check the checkbox to mark as complete
8. **Edit/Delete**: Hover over items to see action buttons

## Offline Mode

- When connection is lost, mutation requests (POST, PATCH, DELETE) are queued
- When connection is restored, queued requests are automatically retried
- Maximum 3 retry attempts per request

## API Base URL

The app connects to `http://localhost:8000` by default. To change this, edit `js/api/client.js`:

```javascript
const API_BASE_URL = 'http://localhost:8000'; // Change this
```

## Browser Compatibility

- Modern browsers with ES6 module support
- Chrome 61+, Firefox 60+, Safari 11+, Edge 16+
