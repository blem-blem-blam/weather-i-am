import pytest
from unittest.mock import AsyncMock, MagicMock, ANY

from app.models.user_model import Users
from app.services.user_service import UserService, UserDataManager
from app.services.auth_service import AuthMixin


@pytest.mark.asyncio
class TestUserService:
    @pytest.fixture
    def mock_data_manager(self):
        """Provides a mock for the UserDataManager."""
        return AsyncMock()

    @pytest.fixture
    def mock_user_parameter_service(self):
        """Provides a mock for the UserParameterService."""
        return AsyncMock()

    @pytest.fixture
    def user_service(self, mock_data_manager, mock_user_parameter_service):
        """Provides an instance of UserService with mocked dependencies."""
        return UserService(
            data_manager=mock_data_manager,
            user_parameter_service=mock_user_parameter_service,
        )

    async def test_get_user(self, user_service, mock_data_manager):
        """Tests that get_user calls the data manager correctly."""
        username = "testuser"
        await user_service.get_user(username)
        mock_data_manager.get_user_by_user_name.assert_called_once_with(username)

    async def test_add_user(
        self, user_service, mock_data_manager, mock_user_parameter_service
    ):
        """
        Tests that adding a user also triggers adding user parameters.
        """
        username = "newuser"
        email = "new@example.com"
        password = "password123"

        # The user object is created inside the service, so we can't know the ID ahead of time.
        # We can assert that the parameter service was called with the user object's ID.
        result_user = await user_service.add_user(username, email, password)

        # Assert user was added via data manager
        mock_data_manager.add_user.assert_called_once()
        added_user_arg = mock_data_manager.add_user.call_args[0][0]
        assert isinstance(added_user_arg, Users)
        assert added_user_arg.username == username

        # Assert parameter service was called with the new user's ID
        mock_user_parameter_service.add_parameter.assert_called_once_with(
            result_user.id
        )
        assert result_user.username == username


@pytest.mark.asyncio
class TestUserDataManager:
    @pytest.fixture
    def mock_session(self):
        """Provides a mock for the AsyncSession."""
        session = MagicMock()
        session.add = MagicMock()
        session.scalar = AsyncMock()
        session.flush = AsyncMock()
        return session

    @pytest.fixture
    def datamanager(self, mock_session):
        """Provides an instance of UserDataManager with a mocked session."""
        return UserDataManager(session=mock_session)

    async def test_add_user(self, datamanager, mock_session):
        """Tests that adding a user calls session.add and session.flush."""
        user = Users(username="test", email="test@test.com", hashed_password="hash")
        await datamanager.add_user(user)
        mock_session.add.assert_called_once_with(user)
        mock_session.flush.assert_called_once()

    async def test_get_user_by_user_name(self, datamanager, mock_session):
        """Tests that getting a user calls the session's scalar method correctly."""
        username = "testuser"
        await datamanager.get_user_by_user_name(username)
        mock_session.scalar.assert_called_once_with(ANY)
