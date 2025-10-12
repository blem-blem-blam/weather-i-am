import uuid

from sqlalchemy import select
from app.models.user_parameter_model import (
    UserParameter,
    UserParameterBase,
    UserParameterUpdate,
)
from app.services.auth_service import AuthService
from app.services.base import BaseService, BaseDataManager


class UserParameterService(BaseService):

    async def add_parameter(
        self, user_id: uuid.UUID, parameter: UserParameterUpdate = None
    ) -> UserParameter:
        user_parameters_base = user_parameters = (
            UserParameterBase(preferred_lat=-36.15, preferred_lon=95.98)
            if not parameter
            else UserParameterBase(**parameter.model_dump())
        )

        user_parameters = UserParameter(
            user_id=user_id, **user_parameters_base.model_dump()
        )

        return await UserParameterDatamanager(self.session).add_user_parameters(
            user_parameters
        )

    async def get_user_params_by_user_id(self, user_id: uuid.UUID) -> UserParameter:
        return await UserParameterDatamanager(self.session).get_user_params_by_user_id(
            user_id
        )


class UserParameterDatamanager(BaseDataManager):
    async def add_user_parameters(self, user_parameters: UserParameter) -> None:
        """Adds a user_parameters object to the session."""
        self.add_one(user_parameters)

    async def get_user_params_by_user_id(self, user_id: uuid.UUID) -> UserParameter:
        return await self.get_one(
            select(UserParameter).where(UserParameter.user_id == user_id)
        )
