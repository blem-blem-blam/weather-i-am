# tests/conftest.py
from httpx import ASGITransport, AsyncClient
import pytest
import pytest_asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

from app.config import settings
from app.database.session import get_db_session
from app.models import User, UserParameter

# Import your actual FastAPI app
from app.main import app  # Adjust this import to your actual app location


@pytest_asyncio.fixture(scope="function")
async def engine() -> AsyncGenerator[AsyncEngine, None]:
    """Create async engine for each test function."""
    engine = create_async_engine(
        str(settings.ASYNC_SQL_DATABASE_URI),
        echo=True,
        poolclass=None,  # Use NullPool to avoid connection reuse issues
    )

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    yield engine

    # Drop tables
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture()
async def session(engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    """
    Creates a new session for each test, wrapped in a transaction that is
    rolled back at the end of the test.
    """
    # The connection is automatically closed and the transaction is rolled back
    # when the 'async with' block exits, even if an error occurs.
    async with engine.connect() as connection:
        async with connection.begin() as transaction:
            async_session_maker = sessionmaker(
                bind=connection, class_=AsyncSession, expire_on_commit=False
            )
            async with async_session_maker() as test_session:
                yield test_session
            # The transaction is rolled back here when this 'with' block exits
            # because we don't call transaction.commit()


@pytest_asyncio.fixture()
async def client(
    engine: AsyncEngine, session: AsyncSession
) -> AsyncGenerator[AsyncClient, None]:
    """
    Creates a test client that uses the test database session.
    """

    async def get_test_session() -> AsyncGenerator[AsyncSession, None]:
        yield session

    app.dependency_overrides[get_db_session] = get_test_session

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as test_client:
        yield test_client

    app.dependency_overrides.clear()
