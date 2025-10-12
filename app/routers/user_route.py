from fastapi import APIRouter, Depends
from sqlmodel import Session
from app.database.session import get_db_session
from app.services.user_service import UserService


router = APIRouter()


@router.post("", response_model=None)
async def create_user(
    username: str,
    email: str,
    password: str,
    db_session: Session = Depends(get_db_session),
) -> None:
    """
    Create a new user. This is a placeholder implementation.
    In a real application, you would save the user to the database.
    """
    _ = await UserService(db_session).add_user(username, email, password)
    return None
