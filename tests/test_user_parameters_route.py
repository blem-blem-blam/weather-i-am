import pytest
import uuid
from httpx import AsyncClient
from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.database.session import get_db_session
from app.models.user_model import User
from app.models.user_parameter_model import UserParameter


@pytest.mark.asyncio
async def test_get_user_params_not_found(session: AsyncSession, client: AsyncClient):
    """
    Test retrieving parameters for a non-existent user.
    """
    non_existent_user_id = uuid.uuid4()
    response = await client.get(f"/v1/user_parameters/{non_existent_user_id}")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
