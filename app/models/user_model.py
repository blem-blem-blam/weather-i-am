import uuid
from enum import Enum
from sqlmodel import Field, SQLModel
from sqlalchemy import Column, Enum as SAEnum


class CustomRoles(str, Enum):
    ADMIN = "admin"
    PREMIUM = "premium"
    BASIC = "basic"
    UNCONFIRMED = "unconfirmed"
    ANONYMOUS_PERMANENT = "anonymous_permanent"
    ANONYMOUS = "anonymous"


class Scope(str, Enum):
    READ_UNPAID = "content_unpaid:read"
    WRITE_UNPAID = "content_unpaid:write"
    READ_PAID = "content_paid:read"
    WRITE_PAID = "content_paid:write"
    ADMIN = "admin"


class UserBase(SQLModel):
    username: str = Field(unique=True, index=True)
    email: str = Field(unique=True, index=True)
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)


class Users(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    auth_role: CustomRoles = Field(
        sa_column=Column(SAEnum(CustomRoles, name="custom_roles"), nullable=False),
        default=CustomRoles.ANONYMOUS,
    )


class UserCreate(SQLModel):
    username: str
    email: str
    password: str
