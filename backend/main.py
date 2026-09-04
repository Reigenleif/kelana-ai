import sys
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Ensure backend directory is in sys.path for direct imports
backend_dir = str(Path(__file__).resolve().parent)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

try:
    from config import settings
    from database import init_db
    from migrate_seed import run_migration_and_seed
    from routers import (
        auth_router,
        chat_router,
        recommendations_router,
        trips_router,
    )
except ImportError:
    from backend.config import settings
    from backend.database import init_db
    from backend.migrate_seed import run_migration_and_seed
    from backend.routers import (
        auth_router,
        chat_router,
        recommendations_router,
        trips_router,
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager: initializes database tables and runs migrations/seeds on startup.
    """
    init_db()
    try:
        run_migration_and_seed()
    except Exception as e:
        print(f"Migration / seed info: {e}")
    yield


app = FastAPI(
    title=settings.app_name,
    description="Smart travel itinerary planning, AI recommendations, authentication & AI assistant chat.",
    version=settings.app_version,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount modular routers
app.include_router(auth_router)
app.include_router(trips_router)
app.include_router(chat_router)
app.include_router(recommendations_router)


# --- Root / Health check ---
@app.get("/", tags=["System"])
async def root():
    return {
        "message": f"Welcome to {settings.app_name} v{settings.app_version}",
        "status": "online",
        "docs": "/docs",
    }


@app.get("/health", tags=["System"])
async def health():
    return {
        "status": "healthy",
        "version": settings.app_version,
        "environment": settings.environment,
    }


def start():
    """CLI entrypoint to run the FastAPI development server."""
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    start()
