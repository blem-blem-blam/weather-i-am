from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db_session
from app.services.user_service import UserService, get_user_service
from app.models.user_model import UserCreate

router = APIRouter()


@router.post("", response_model=None)
async def create_user(
    user_data: UserCreate,
    user_service: UserService = Depends(get_user_service),
    db_session: AsyncSession = Depends(get_db_session),
) -> None:
    """
    Create a new user and their default parameters.
    """
    await user_service.add_user(user_data.username, user_data.email, user_data.password)
    # Commit the transaction after all operations are added to the session
    await db_session.commit()
    return None
