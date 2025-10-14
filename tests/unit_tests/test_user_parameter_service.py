import pytest
import uuid
from unittest.mock import AsyncMock, MagicMock, ANY

from app.models.user_parameter_model import UserParameter, UserParameterUpdate
from app.services.user_parameter_service import (
    UserParameterService,
    UserParameterDatamanager,
)


@pytest.mark.asyncio
class TestUserParameterService:
    @pytest.fixture
    def mock_data_manager(self):
        """Provides a mock for the UserParameterDataManager."""
        return AsyncMock()

    @pytest.fixture
    def user_parameter_service(self, mock_data_manager):
        """Provides an instance of UserParameterService with a mocked data manager."""
        return UserParameterService(data_manager=mock_data_manager)

    async def test_add_parameter_with_defaults(
        self, user_parameter_service, mock_data_manager
    ):
        """Tests adding parameters with default values when none are provided."""
        user_id = uuid.uuid4()
        mock_data_manager.add_user_parameters.return_value = UserParameter(
            user_id=user_id, preferred_lat=-36.15, preferred_lon=95.98
        )

        result = await user_parameter_service.add_parameter(user_id)

        mock_data_manager.add_user_parameters.assert_called_once()
        call_args = mock_data_manager.add_user_parameters.call_args[0][0]
        assert isinstance(call_args, UserParameter)
        assert call_args.user_id == user_id
        assert call_args.preferred_lat == -36.15  # Default value
        assert result.preferred_lat == -36.15

    async def test_add_parameter_with_custom_values(
        self, user_parameter_service, mock_data_manager
    ):
        """Tests adding parameters with custom provided values."""
        user_id = uuid.uuid4()
        custom_params = UserParameterUpdate(preferred_lat=50.0, preferred_lon=-100.0)
        mock_data_manager.add_user_parameters.return_value = UserParameter(
            user_id=user_id, **custom_params.model_dump()
        )

        result = await user_parameter_service.add_parameter(user_id, custom_params)

        mock_data_manager.add_user_parameters.assert_called_once()
        call_args = mock_data_manager.add_user_parameters.call_args[0][0]
        assert isinstance(call_args, UserParameter)
        assert call_args.user_id == user_id
        assert call_args.preferred_lat == 50.0
        assert result.preferred_lon == -100.0

    async def test_get_user_params_by_user_id(
        self, user_parameter_service, mock_data_manager
    ):
        """Tests retrieving user parameters by user ID."""
        user_id = uuid.uuid4()
        await user_parameter_service.get_user_params_by_user_id(user_id)
        mock_data_manager.get_user_params_by_user_id.assert_called_once_with(user_id)


@pytest.mark.asyncio
class TestUserParameterDatamanager:
    @pytest.fixture
    def mock_session(self):
        """Provides a mock for the AsyncSession."""
        session = MagicMock()
        session.add = MagicMock()
        session.scalar = AsyncMock()
        return session

    @pytest.fixture
    def datamanager(self, mock_session):
        """Provides an instance of UserParameterDatamanager with a mocked session."""
        return UserParameterDatamanager(session=mock_session)

    async def test_add_user_parameters(self, datamanager, mock_session):
        """Tests that adding parameters calls the session's add method."""
        params = UserParameter(
            user_id=uuid.uuid4(), preferred_lat=1.0, preferred_lon=1.0
        )
        await datamanager.add_user_parameters(params)
        mock_session.add.assert_called_once_with(params)

    async def test_get_user_params_by_user_id(self, datamanager, mock_session):
        """Tests that getting parameters calls the session's scalar method correctly."""
        user_id = uuid.uuid4()
        await datamanager.get_user_params_by_user_id(user_id)
        mock_session.scalar.assert_called_once()
        # ANY is used because the select statement object is complex to reconstruct
        mock_session.scalar.assert_called_with(ANY)
