# tests/conftest.py

from httpx import ASGITransport, AsyncClient
import pytest_asyncio
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from httpx import AsyncClient
from fastapi import Depends, FastAPI

# Import the application's settings object
from app.config import settings
from app.database.session import get_db_session
from app.models import User, UserParameter  # IMPORTANT: Import all your models!

app = FastAPI()


# Create an async engine fixture.
# The `scope="session"` means the engine is created once for the entire test session.
@pytest_asyncio.fixture(scope="session")
def engine():
    # settings.ASYNC_SQL_DATABASE_URI will be loaded from .env.test
    # because the TESTING env var is set.
    return create_async_engine(str(settings.ASYNC_SQL_DATABASE_URI))


# An async fixture to automatically create and drop tables.
# This runs once before all tests and once after all tests have completed.
@pytest_asyncio.fixture(scope="session", autouse=True)
async def create_drop_tables(engine):
    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(SQLModel.metadata.create_all)

    yield  # The tests run here

    async with engine.begin() as conn:
        # Drop all tables
        await conn.run_sync(SQLModel.metadata.drop_all)


# A fixture that creates a new session for each test function.
@pytest_asyncio.fixture()
async def session(engine) -> AsyncGenerator[AsyncSession, None]:
    # The sessionmaker is configured for async sessions
    async_session_maker = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session_maker() as session:
        yield session


@pytest_asyncio.fixture()
async def client(session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    Creates a test client that uses the test database.
    """

    # This is the override function. It will replace your `get_session`
    # dependency in the main app with the test session.
    async def get_test_session() -> AsyncGenerator[AsyncSession, None]:
        yield session

    # Apply the dependency override
    app.dependency_overrides[get_db_session] = get_test_session

    # Create and yield the test client
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client

    # Clean up the override after the test is done
    app.dependency_overrides.clear()
