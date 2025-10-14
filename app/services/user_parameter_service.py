import uuid
from abc import ABC, abstractmethod

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user_parameter_model import (
    UserParameter,
    UserParameterBase,
    UserParameterUpdate,
)
from app.services.base import BaseDataManager


class IUserParameterDataManager(ABC):
    @abstractmethod
    async def add_user_parameters(
        self, user_parameters: UserParameter
    ) -> UserParameter:
        pass

    @abstractmethod
    async def get_user_params_by_user_id(
        self, user_id: uuid.UUID
    ) -> UserParameter | None:
        pass


class IUserParameterService(ABC):
    @abstractmethod
    async def add_parameter(
        self, user_id: uuid.UUID, parameter: UserParameterUpdate = None
    ) -> UserParameter:
        pass

    @abstractmethod
    async def get_user_params_by_user_id(
        self, user_id: uuid.UUID
    ) -> UserParameter | None:
        pass


class UserParameterService(IUserParameterService):
    def __init__(self, data_manager: IUserParameterDataManager):
        self.data_manager = data_manager

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

        return await self.data_manager.add_user_parameters(user_parameters)

    async def get_user_params_by_user_id(
        self, user_id: uuid.UUID
    ) -> UserParameter | None:
        return await self.data_manager.get_user_params_by_user_id(user_id)


class UserParameterDatamanager(BaseDataManager, IUserParameterDataManager):
    async def add_user_parameters(
        self, user_parameters: UserParameter
    ) -> UserParameter:
        self.add_one(user_parameters)
        return user_parameters

    async def get_user_params_by_user_id(
        self, user_id: uuid.UUID
    ) -> UserParameter | None:
        return await self.get_one(
            select(UserParameter).where(UserParameter.user_id == user_id)
        )
