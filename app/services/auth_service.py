from datetime import datetime, timedelta, timezone

from typing import Annotated, List
import uuid
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from sqlmodel import select
from app.models.user_model import CustomRoles, Scope, Users
from passlib.context import CryptContext
import jwt

from app.services.base import BaseService, BaseDataManager
from ..config import settings

scopes = {
    CustomRoles.ADMIN: [
        Scope.READ_UNPAID.name,
        Scope.WRITE_UNPAID.name,
        Scope.READ_PAID.name,
        Scope.WRITE_PAID.name,
        Scope.ADMIN.name,
    ],
    CustomRoles.PREMIUM: [
        Scope.READ_UNPAID.name,
        Scope.WRITE_UNPAID.name,
        Scope.READ_PAID.name,
        Scope.WRITE_PAID.name,
    ],
    CustomRoles.BASIC: [Scope.READ_UNPAID.name, Scope.WRITE_UNPAID.name],
    CustomRoles.UNCONFIRMED: [Scope.READ_UNPAID.name],
    CustomRoles.ANONYMOUS_PERMANENT: [Scope.READ_UNPAID.name],
    CustomRoles.ANONYMOUS: [Scope.READ_PAID.name],
}

oauth2_scopes = {
    "content_unpaid:read": "Read access to unpaid content",
    "content_unpaid:write": "Write access to unpaid content",
    "content_paid:read": "Read access to paid content",
    "content_paid:write": "Write access to paid content",
    "admin": "Admin access",
}

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
ph = PasswordHasher()


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    sub: str  # The 'subject' of the token, which we use for the username.
    scopes: List[str] = []


class AuthMixin:
    @staticmethod
    def get_scopes_for_role(role: str) -> list[str]:
        return scopes.get(role, [])

    @staticmethod
    def verify_argon2_password(plain_password, hashed_password) -> bool:
        try:
            ph.verify(hashed_password, plain_password)
            return True
        except VerifyMismatchError as e:
            raise e
        except (TypeError, ValueError) as e:
            raise e
        except Exception as e:
            raise e

    @staticmethod
    def get_password_hash(password) -> str:
        return ph.hash(password)

    @staticmethod
    def create_access_token(data: dict, expires_delta: timedelta | None = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM
        )
        return encoded_jwt

    @staticmethod
    def generate_token_for_user(user: Users) -> Token:
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = AuthService.create_access_token(
            data={
                "sub": user.username,
                "scopes": " ".join(AuthService.get_scopes_for_role(user.auth_role)),
            },
            expires_delta=access_token_expires,
        )
        return Token(access_token=access_token, token_type="bearer")


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/auth/token", scopes=oauth2_scopes)


class AuthService(BaseService, AuthMixin):
    def authenticate_user(self, user: Users, password: str) -> Token | bool:
        if not user:
            return False
        if not AuthMixin.verify_argon2_password(password, user.hashed_password):
            return False
        return AuthMixin.generate_token_for_user(user)


async def decode_user_jwt(
    token: Annotated[str, Depends(oauth2_scheme)],
) -> TokenPayload:
    """
    Dependency to get the current active user from a JWT token.
    1. Decodes the JWT token.
    2. Validates the payload.
    3. Returns the payload as a readable object.

    This does not guarantee user has scope authority or if they exist in the database
    """
    invalid_jwt_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not decode the JWT",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        # The 'scopes' in the JWT is a space-delimited string.
        token_scopes = payload.get("scopes", "").split()
        token_data = TokenPayload(sub=payload.get("sub"), scopes=token_scopes)

        return token_data

    except (jwt.PyJWTError, TypeError, KeyError):
        # If decoding fails or payload is malformed, raise the 401 exception.
        raise invalid_jwt_exception
