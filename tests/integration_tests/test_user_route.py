import pytest
import uuid
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.user_parameter_service import UserParameterService
from app.services.user_service import UserDataManager, UserService
from .conftest import client
from app.services.user_parameter_service import (
    UserParameterDatamanager,
    UserParameterService,
)


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
    user_data_manager = UserDataManager(session)
    user_param_service = UserParameterService(UserParameterDatamanager(session))
    user_service = UserService(user_data_manager, user_param_service)
    await user_service.add_user("test_user", "test@test.com", "test_password")

    # We don't commit in tests, so the transaction is rolled back.
    # The user service now handles its own commit logic, so we just call it.
    # The test session override handles the transaction.

    user = await user_service.get_user("test_user")

    # Now make the request - it will use the same session/transaction
    response = await client.get(f"/v1/user_parameters/{user.id}")

    assert response.status_code == 200
    assert response.json()["user_id"] == str(user.id)
    assert response.json()["id"]
    assert response.json()["time_created"]
