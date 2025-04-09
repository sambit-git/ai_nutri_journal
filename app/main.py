from contextlib import asynccontextmanager
import os
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.database import engine
from app.models.base import Base

# Import all routers
from app.api.endpoints.auth import router as auth_router
from app.api.endpoints.meal import router as meals_router
from app.api.endpoints.nutrition import router as nutrition_router
from app.middlewares.logger import LoggingMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Async context manager for app lifespan events"""
    # Startup logic
    if settings.CREATE_TABLES:
        Base.metadata.create_all(bind=engine)
        print("Database tables created")
    
    yield  # App runs here
    
    # Shutdown logic would go here
    # (e.g., await database.disconnect())


def create_app():
    """Application factory pattern"""
    app = FastAPI(
        title="NutriJournal",
        description="Nutrition tracking application",
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/docs" if settings.DEBUG else None,  # Disable docs in production
        redoc_url=None
    )

    # Setup middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(LoggingMiddleware)

    # Mount static files
    if not os.path.exists(settings.STATIC_FILES_DIR):
        os.makedirs(settings.STATIC_FILES_DIR)
    app.mount(
        "/static",
        StaticFiles(directory=settings.STATIC_FILES_DIR),
        name="static"
    )

    # Include all API routers
    app.include_router(auth_router)
    app.include_router(meals_router)
    app.include_router(nutrition_router)

    @app.get("/health", include_in_schema=False)
    async def health_check():
        """Liveness probe"""
        return {"status": "healthy"}

    return app

# Create application instance
app = create_app()