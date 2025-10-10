from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import create_async_engine

from app.routers import love_yourself, user_route

from .routers import user_auth_route, user_parameters_route
from .config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handles startup and shutdown events for the application.
    """
    # === STARTUP ===
    print("🚀 Application starting up...")

    # Create the PostgreSQL connection pool (engine)
    app.state.db_engine = create_async_engine(
        str(settings.ASYNC_SQL_DATABASE_URI), echo=True, future=True
    )
    print("PostgreSQL connection pool created.")

    yield  # The application is now running

    # === SHUTDOWN ===
    print("👋 Application shutting down...")

    # Dispose of the PostgreSQL engine
    await app.state.db_engine.dispose()
    print("PostgreSQL connection pool closed.")


app = FastAPI(lifespan=lifespan)

app.include_router(love_yourself.router, prefix="")
app.include_router(user_auth_route.router, prefix="/v1/auth")
app.include_router(user_parameters_route.router, prefix="/v1/user_parameters")
app.include_router(user_route.router, prefix="/v1/users")
