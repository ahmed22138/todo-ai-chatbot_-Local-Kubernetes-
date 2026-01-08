"""Database connection pool setup with async PostgreSQL."""

import os
from typing import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://todo_user:todo_password@localhost:5432/todo_chatbot")

# Create async engine with connection pooling
engine: AsyncEngine = create_async_engine(
    DATABASE_URL,
    echo=os.getenv("ENVIRONMENT") == "development",
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,  # Verify connections before using
    pool_recycle=3600,   # Recycle connections after 1 hour
)

# Async session maker
async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def init_db() -> None:
    """Initialize database tables.

    Creates all tables defined in SQLModel metadata.
    Used for testing and local development.
    In production, use Alembic migrations.
    """
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting async database session.

    Yields:
        AsyncSession: Database session that auto-closes after use.

    Example:
        @app.get("/items")
        async def get_items(session: AsyncSession = Depends(get_session)):
            result = await session.execute(select(Item))
            return result.scalars().all()
    """
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def check_db_health() -> bool:
    """Check database connection health.

    Returns:
        bool: True if database is reachable and healthy.

    Raises:
        Exception: If database connection fails.
    """
    try:
        async with engine.connect() as conn:
            await conn.scalar(text("SELECT 1"))
        return True
    except Exception as e:
        raise Exception(f"Database health check failed: {str(e)}")
