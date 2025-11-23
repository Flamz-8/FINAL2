"""FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.study_helper.core.config import settings
from src.study_helper.api import auth, courses, notes, tasks

app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    description="Personal knowledge management app for students",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": settings.APP_NAME}


# Include routers
app.include_router(auth.router)
app.include_router(courses.router)
app.include_router(notes.router)
app.include_router(tasks.router)
