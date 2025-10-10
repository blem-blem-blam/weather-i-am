from typing import AsyncGenerator
from fastapi import Request
from sqlalchemy import create_engine
from sqlalchemy.orm import (
    sessionmaker,
)

from sqlalchemy.ext.asyncio import AsyncSession

from ..config import settings

# create session factory to generate new database sessions
SessionFactory = sessionmaker(
    bind=create_engine(str(settings.ASYNC_SQL_DATABASE_URI)),
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


async def get_db_session(request: Request) -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting a PostgreSQL session.
    It's created for each request and closed after.
    """
    # The engine was created in the lifespan manager and stored in app.state
    engine = request.app.state.db_engine

    async with AsyncSession(engine) as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
