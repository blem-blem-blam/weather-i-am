from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated
from fastapi.params import Security
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session
from app.database.session import get_db_session
from app.models.user_model import User
from ..services.auth_service import (
    AuthService,
    Token,
    decode_user_jwt,
)

from ..services.user_service import UserService


router = APIRouter(dependencies=[Depends(get_db_session)])


@router.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db_session: Session = Depends(get_db_session),
) -> Token:
    """
    Authenticate user and return an access token if credentials are valid.
    """
    retrieved_user = await UserService(db_session).get_user(form_data.username)

    if not retrieved_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    token = AuthService(db_session).authenticate_user(
        retrieved_user, form_data.password
    )
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token


@router.get("/me/", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(decode_user_jwt)],
):
    """
    Get the details for the currently authenticated user.
    """
    return current_user


@router.get("/me/scopes", response_model=list[str])
async def read_users_me(
    # This is the only line that changes
    current_user: Annotated[User, Security(decode_user_jwt, scopes=["admin"])],
    db_session: Session = Depends(get_db_session),
) -> list[str]:
    """
    Get the scopes for the currently authenticated user's role.
    Requires "admin" scope.
    """
    return AuthService(db_session).get_scopes_for_role(current_user.role)


# @router.post("/auth/anonymous", response_model=Token)
# async def register_anonymous_user():
#     """
#     Creates a new anonymous user in the database and returns a JWT.
#     """
#     # Create the user document
#     new_user = User(is_anonymous=True)
#     await new_user.insert()

#     # Create a long-lived token for them
#     expires = timedelta(minutes=1)
#     access_token = create_access_token(
#         data={"sub": str(new_user.id)}, expires_delta=expires
#     )

#     return {"access_token": access_token, "token_type": "bearer"}


# In a file like app/routers/forecast.py
