"""
Database Connection and Session Management

Provides database connection, session management, and migration utilities.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from typing import Generator, AsyncGenerator
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

# Convert database URL for sync operations (Alembic, scripts)
def get_sync_database_url() -> str:
    """Get synchronous database URL for Alembic and scripts."""
    url = settings.DATABASE_URL
    if url and url.startswith("postgresql+asyncpg://"):
        return url.replace("postgresql+asyncpg://", "postgresql://")
    elif url and url.startswith("postgresql://"):
        return url
    else:
        # Construct from components (should not happen due to model_validator)
        return (
            f"postgresql://{settings.DB_USER}:{settings.DB_PASSWORD}@"
            f"{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
        )

# Synchronous engine for Alembic, scripts, and background workers.
# Use a conservative connection pool so we don't exhaust Azure Postgres slots.
sync_engine = create_engine(
    get_sync_database_url(),
    pool_pre_ping=True,
    pool_size=5,        # max 5 connections per process
    max_overflow=0,     # don't create extra connections beyond pool_size
    pool_recycle=1800,  # recycle connections every 30 minutes
    echo=settings.DEBUG,
)

# Async engine for FastAPI
async_engine = None
if settings.DATABASE_URL and settings.DATABASE_URL.startswith("postgresql+asyncpg://"):
    async_engine = create_async_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=0,
        pool_recycle=1800,
        echo=settings.DEBUG,
    )

# Session makers
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=sync_engine
)

AsyncSessionLocal = None
if async_engine:
    AsyncSessionLocal = async_sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )


def get_db() -> Generator[Session, None, None]:
    """
    Dependency for getting database session (synchronous).
    
    Usage in FastAPI:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting async database session.
    
    Usage in FastAPI:
        @app.get("/items")
        async def get_items(db: AsyncSession = Depends(get_async_db)):
            ...
    """
    if not AsyncSessionLocal:
        raise RuntimeError("Async database not configured. Check DATABASE_URL.")
    
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
