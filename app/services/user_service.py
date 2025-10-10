import uuid
from sqlmodel import select
from app.models.user_model import User
from app.services.auth_service import AuthService
from app.services.base import BaseService, BaseDataManager
from app.services.user_parameter_service import UserParameterService


class UserService(BaseService):

    async def get_user(self, username: str) -> User | None:
        return await UserDataManager(self.session).get_user_by_user_name(username)

    async def add_user(self, username: str, email: str, password: str) -> None:
        user_to_add = User(
            username=username,
            email=email,
            hashed_password=AuthService.get_password_hash(password),
            is_active=True,
            is_superuser=False,
        )
        await UserDataManager(self.session).add_user(user_to_add)
        await UserParameterService(self.session).add_parameter(user_to_add.id)
        await self.session.commit()


class UserDataManager(BaseDataManager):
    async def get_user(self, user_id: uuid.UUID) -> User | None:
        select_stmt = select(User).where(User.id == user_id)
        return await self.get_one(select_stmt)

    async def get_user_by_user_name(self, user_name: str) -> User | None:
        select_stmt = select(User).where(User.username == user_name)
        return await self.get_one(select_stmt)

    async def add_user(self, user: User) -> None:
        self.add_one(user)
        await self.session.flush()
        await self.session.refresh(user)
