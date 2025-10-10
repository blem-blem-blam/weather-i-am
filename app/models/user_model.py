from enum import Enum
from sqlmodel import SQLModel, Field, Column, TIMESTAMP
from datetime import datetime
from sqlalchemy import func
import uuid
from pydantic import BaseModel, EmailStr
from pydantic import EmailStr


class CustomRoles(str, Enum):
    ADMIN = "admin"
    PREMIUM = "premium"
    BASIC = "basic"
    UNCONFIRMED = "unconfirmed"
    ANONYMOUS_PERMANENT = "anonymous_permanent"  # long-lived anonymous user
    ANONYMOUS = "anonymous"


class Scope(str, Enum):
    """
    Scope defines the available permission levels for user actions.

    Attributes:
        READ_UNPAID: Allows 3 hourly forecasts ("content_unpaid:read").
        WRITE_UNPAID: Allows limited voting ("content_unpaid:write").
        READ_PAID: Allows hourly forecasts ("content_paid:read").
        WRITE_PAID: Allows premium votes("content_paid:write").
        ADMIN: Grants all administrative permissions ("admin:all").
    """

    READ_UNPAID = "content_unpaid:read"
    WRITE_UNPAID = "content_unpaid:write"
    READ_PAID = "content_paid:read"
    WRITE_PAID = "content_paid:write"
    ADMIN = "admin:all"


class UserBase(SQLModel):
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4, primary_key=True, index=True, unique=True
    )
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    username: str = Field(index=True, unique=True)
    auth_role: CustomRoles = Field(default=CustomRoles.ANONYMOUS)


class User(UserBase, table=True):
    __tablename__ = "users"
    is_active: bool = True
    is_anonymous: bool = False
    is_superuser: bool = False
    hashed_password: str
    # last_access: datetime | None = None
    # associated_IP_address: str | None = None
    time_created: datetime | None = Field(
        default=None,
        sa_column=Column(
            TIMESTAMP(timezone=True),
            server_default=func.now(),
            nullable=False,
            index=True,
        ),
    )
    time_updated: datetime | None = Field(
        default=None,
        sa_column=Column(
            TIMESTAMP(timezone=True),
            server_default=func.now(),
            onupdate=func.now(),
            nullable=False,
            index=True,
        ),
    )


class UserResponse(BaseModel):
    pass
