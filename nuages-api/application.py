from contextlib import asynccontextmanager

from fastapi import FastAPI

from .database import init_db


@asynccontextmanager
async def lifespan(application: FastAPI):
    """Lifespan context to initialize database on startup."""
    init_db()
    yield


class Application(FastAPI):
    """Custom FastAPI application for Nuages management."""

    def __init__(self):
        super().__init__(
            title="Nuages Management API",
            description="API for managing Nuages resources",
            version="0.1.0",
            lifespan=lifespan,
        )
        init_db()  # Initialize the database when the application starts
