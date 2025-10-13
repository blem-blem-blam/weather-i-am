import uuid

from fastapi import APIRouter, Depends, HTTPException, Path, Body, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.database.session import get_db_session
from app.models.user_parameter_model import (
    UserParameter,
    UserParameterUpdate,
)
from app.services.user_parameter_service import (
    UserParameterDatamanager,
    UserParameterService,
)

router = APIRouter(tags=["User Parameters"])


@router.get("/{user_id}", response_model=UserParameter)
async def get_user_params_by_user_id(
    *,
    session: AsyncSession = Depends(get_db_session),
    user_id: uuid.UUID = Path(..., description="The ID of the user to retrieve."),
):
    """
    Retrieve the notification parameters for a specific user.
    """
    service = UserParameterService(UserParameterDatamanager(session))
    return await service.get_user_params_by_user_id(user_id)


@router.patch("/{user_id}", response_model=UserParameter)
async def update_user_params(
    *,
    session: AsyncSession = Depends(get_db_session),
    user_id: uuid.UUID = Path(..., description="The ID of the user to update."),
    patch_params: UserParameterUpdate = Body(
        ..., description="The parameter fields to update."
    ),
):
    """
    Update a user's notification parameters.

    Only the fields provided in the request body will be updated.
    """
    db_user_params = (
        await session.execute(
            select(UserParameter).where(UserParameter.user_id == user_id)
        )
    ).scalar_one_or_none()

    if not db_user_params:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User parameters not found for user_id: {user_id}",
        )

    patch_data = patch_params.model_dump(exclude_unset=True)
    for key, value in patch_data.items():
        setattr(db_user_params, key, value)

    session.add(db_user_params)
    await session.commit()
    await session.refresh(db_user_params)
    return db_user_params
