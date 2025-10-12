import pytest
from httpx import AsyncClient
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.fixture
def test_user_credentials() -> dict:
    """Provides a standard set of user credentials for tests."""
    return {
        "username": "test_user",
        "password": "test_password",
        "email": "test@test.com",
    }


@pytest_asyncio.fixture
async def created_user(client: AsyncClient, test_user_credentials: dict) -> dict:
    """
    A fixture that creates a user via the API endpoint before a test runs.
    Returns the credentials of the created user.
    """
    response = await client.post("/v1/users", params=test_user_credentials)
    assert response.status_code == 200, "Failed to create user in fixture"
    return test_user_credentials


@pytest.mark.asyncio
async def test_login_for_access_token(client: AsyncClient, created_user: dict):
    """
    Test that a user can successfully log in and receive an access token.
    """
    # Act
    response = await client.post(
        "/v1/auth/token",
        data={
            "username": created_user["username"],
            "password": created_user["password"],
        },
    )

    # Assert
    assert response.status_code == 200
    response_data = response.json()
    assert "access_token" in response_data
    assert response_data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_get_current_user(client: AsyncClient, created_user: dict):
    """
    Test that the /me endpoint returns the correct user details for an
    authenticated user.
    """
    # Arrange
    response = await client.post(
        "/v1/auth/token",
        data={
            "username": created_user["username"],
            "password": created_user["password"],
        },
    )
    assert response.status_code == 200

    # Act
    me_response = await client.get(
        "/v1/auth/me",
        headers={
            "Authorization": f"Bearer {response.json()['access_token']}",
            "accept": "application/json",
        },
    )

    # Assert
    assert me_response.status_code == 200
    response_data = me_response.json()
    assert response_data["sub"] == created_user["username"]
    # A new user should have the 'BASIC' role scopes
    assert response_data["scopes"] == ["READ_PAID"]


@pytest.mark.asyncio
async def test_get_current_user_invalid_token(client: AsyncClient):
    """
    Test that the /me endpoint returns a 401 Unauthorized error when an
    invalid token is provided.
    """
    # Act
    me_response = await client.get(
        "/v1/auth/me",
        headers={"Authorization": "Bearer thisisnotavalidtoken"},
    )

    # Assert
    assert me_response.status_code == 401
    assert me_response.json()["detail"] == "Could not decode the JWT"
