import pytest
import uuid
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.user_parameter_service import UserParameterService
from app.services.user_service import UserService
from .conftest import client


from app.main import app


# @pytest.mark.asyncio
# async def test_get_user_params_not_found(client: AsyncClient, session: AsyncSession):
#     """
#     Test retrieving parameters for a non-existent user.
#     """
#     non_existent_user_id = uuid.uuid4()
#     response = await client.get(f"/v1/user_parameters/{non_existent_user_id}")
#     assert response.status_code == 404
#     assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_get_user_params(client: AsyncClient, session: AsyncSession):
    """
    Test retrieving parameters for an existing user.
    """
    await UserService(session).add_user(
        username="test_user", email="test@test.com", password="test_password"
    )

    user = await UserService(session).get_user("test_user")

    # Now make the request - it will use the same session/transaction
    response = await client.get(f"/v1/user_parameters/{user.id}")

    assert response.status_code == 200
    assert response.json()["user_id"] == str(user.id)
    assert response.json()["id"]
