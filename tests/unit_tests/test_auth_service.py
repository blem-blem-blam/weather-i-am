import pytest
from unittest.mock import MagicMock
from argon2.exceptions import VerifyMismatchError

from fastapi import HTTPException
import jwt

from app.services.auth_service import (
    AuthService,
    AuthMixin,
    Token,
    TokenPayload,
    decode_user_jwt,
)
from app.models.user_model import Users, CustomRoles


@pytest.fixture
def mock_user():
    """Provides a mock user object for testing."""
    user = Users(
        username="testuser",
        email="test@example.com",
        hashed_password=AuthMixin.get_password_hash("correct_password"),
        auth_role=CustomRoles.BASIC,
    )
    return user


@pytest.fixture
def mock_settings(monkeypatch):
    """Mocks the application settings."""
    monkeypatch.setattr("app.services.auth_service.settings.SECRET_KEY", "test-secret")
    monkeypatch.setattr("app.services.auth_service.settings.JWT_ALGORITHM", "HS256")
    monkeypatch.setattr(
        "app.services.auth_service.settings.ACCESS_TOKEN_EXPIRE_MINUTES", 15
    )
    return


class TestAuthMixin:
    def test_password_hashing_and_verification(self):
        """Tests that password hashing and verification work correctly."""
        password = "mysecretpassword"
        hashed_password = AuthMixin.get_password_hash(password)

        assert isinstance(hashed_password, str)
        assert (
            AuthMixin.verify_argon2_password(password, hashed_password).success is True
        )

        result = AuthMixin.verify_argon2_password("wrongpassword", hashed_password)
        assert result.success is False
        assert isinstance(result.message, str)

    def test_create_access_token(self, mock_settings):
        """Tests the creation of a JWT access token."""
        data = {"sub": "testuser", "scopes": "read write"}
        token = AuthMixin.create_access_token(data)

        decoded_payload = jwt.decode(token, "test-secret", algorithms=["HS256"])

        assert decoded_payload["sub"] == "testuser"
        assert decoded_payload["scopes"] == "read write"
        assert "exp" in decoded_payload

    def test_generate_token_for_user(self, mock_user, mock_settings):
        """Tests generating a full token object for a user."""
        token = AuthMixin.generate_token_for_user(mock_user)
        assert isinstance(token, Token)
        assert token.token_type == "bearer"
        assert isinstance(token.access_token, str)


class TestAuthService:
    @pytest.fixture
    def auth_service(self):
        """Provides an instance of AuthService with a mock session."""
        # The session is not used in the authenticate_user method, so we can pass a mock.
        mock_session = MagicMock()
        return AuthService(session=mock_session)

    def test_authenticate_user_success(self, auth_service, mock_user, mock_settings):
        """Tests successful user authentication."""
        token = auth_service.authenticate_user(mock_user, "correct_password")
        assert isinstance(token, Token)
        assert token.token_type == "bearer"

    def test_authenticate_user_wrong_password(self, auth_service, mock_user):
        """Tests authentication failure with an incorrect password."""
        result = auth_service.authenticate_user(mock_user, "wrong_password")
        assert result is False

    def test_authenticate_user_no_user(self, auth_service):
        """Tests authentication failure when the user object is None."""
        result = auth_service.authenticate_user(None, "any_password")
        assert result is False


@pytest.mark.asyncio
class TestDecodeUserJWT:
    async def test_decode_user_jwt_success(self, mock_settings):
        """Tests successful decoding of a valid JWT."""
        scopes = "read:unpaid"
        token_data = {"sub": "testuser", "scopes": scopes}
        token = AuthMixin.create_access_token(token_data)

        payload = await decode_user_jwt(token)

        assert isinstance(payload, TokenPayload)
        assert payload.sub == "testuser"
        assert payload.scopes == scopes.split()

    async def test_decode_user_jwt_invalid_token(self):
        """Tests that an invalid token raises an HTTPException."""
        with pytest.raises(HTTPException) as exc_info:
            await decode_user_jwt("invalid.token.string")

        assert exc_info.value.status_code == 401
        assert "Could not decode the JWT" in exc_info.value.detail

    async def test_decode_user_jwt_missing_sub(self, mock_settings):
        """Tests that a token missing the 'sub' claim raises an HTTPException."""
        # The Pydantic model `TokenPayload` will raise a validation error,
        # which is caught and re-raised as our custom HTTPException.
        token_data = {"scopes": "read"}  # Missing 'sub'
        token = AuthMixin.create_access_token(token_data)

        with pytest.raises(HTTPException) as exc_info:
            await decode_user_jwt(token)

        assert exc_info.value.status_code == 401
        assert "Could not decode the JWT" in exc_info.value.detail
