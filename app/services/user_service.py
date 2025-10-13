import uuid
from abc import ABC, abstractmethod
from sqlmodel import select
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user_model import Users
from app.services.auth_service import AuthService
from app.services.base import BaseDataManager
from app.database.session import get_db_session
from app.services.user_parameter_service import (
    UserParameterDatamanager,
    UserParameterService,
)


class IUserDataManager(ABC):
    @abstractmethod
    async def get_user_by_user_name(self, user_name: str) -> Users | None:
        pass

    @abstractmethod
    async def add_user(self, user: Users) -> None:
        pass


class UserService:
    def __init__(
        self,
        data_manager: IUserDataManager,
        user_parameter_service: UserParameterService,
    ):
        self.data_manager = data_manager
        self.user_parameter_service = user_parameter_service

    async def get_user(self, username: str) -> Users | None:
        return await self.data_manager.get_user_by_user_name(username)

    async def add_user(self, username: str, email: str, password: str) -> Users:
        user_to_add = Users(
            username=username,
            email=email,
            hashed_password=AuthService.get_password_hash(password),
            is_active=True,
            is_superuser=False,
        )
        # Add the user to the session
        await self.data_manager.add_user(user_to_add)

        # Now create the associated parameters using the new user's ID
        # This relies on the session being flushed within add_user to get the ID
        await self.user_parameter_service.add_parameter(user_to_add.id)
        return user_to_add


class UserDataManager(BaseDataManager, IUserDataManager):
    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get_user_by_user_name(self, user_name: str) -> Users | None:
        select_stmt = select(Users).where(Users.username == user_name)
        return await self.get_one(select_stmt)

    async def add_user(self, user: Users) -> None:
        """Adds a user object to the session."""
        self.add_one(user)
        # Flush to get the ID for subsequent operations like adding parameters
        await self.session.flush()


def get_user_service(
    session: AsyncSession = Depends(get_db_session),
) -> UserService:
    """
    Dependency provider for the UserService.

    This function is responsible for creating and wiring all the necessary
    dependencies for the UserService, including the data managers and
    other services. It keeps this logic out of the route handlers.
    """
    user_param_datamanager = UserParameterDatamanager(session)
    user_param_service = UserParameterService(user_param_datamanager)
    user_datamanager = UserDataManager(session)
    return UserService(
        data_manager=user_datamanager, user_parameter_service=user_param_service
    )
