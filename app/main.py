from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.routes.tutor import router as tutor_router
from app.routes.voice import router as voice_router
from app.routes.quiz import router as quiz_router
from app.routes.auth import router as auth_router
from app.services.database import init_db

# Initialize SQLite database and tables
init_db()

app = FastAPI(
    title="VidyaMitra API",
    description="A Telugu-first multilingual AI learning companion for Class 8 Science.",
    version="1.0.0"
)

# CORS middleware for local development and future web client
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files for UI and generated audio
static_dir = Path("app/static")
static_dir.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Include routers
app.include_router(tutor_router)
app.include_router(voice_router)
app.include_router(quiz_router)
app.include_router(auth_router)


@app.get("/")
async def home():
    """Serves the interactive VidyaMitra browser UI."""
    index_path = Path("app/static/index.html")
    if index_path.exists():
        return FileResponse(str(index_path))
    return {
        "message": "Welcome to VidyaMitra!",
        "status": "running",
        "project": "Telugu-First Multilingual AI Learning Companion",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "backend": "FastAPI",
        "version": "1.0.0"
    }
