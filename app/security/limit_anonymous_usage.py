from app.models.user_model import User
from .token_master import get_current_user
from fastapi import Depends, HTTPException, status

# Set your desired limit
ANONYMOUS_REQUEST_LIMIT = 50


async def limit_anonymous_usage(current_user: User = Depends(get_current_user)):
    """
    A dependency that checks usage limits for anonymous users.
    """
    # If there's no user at all, they MUST get an anonymous token first.
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token required.",
        )

    if current_user.is_anonymous:
        if current_user.request_count >= ANONYMOUS_REQUEST_LIMIT:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usage limit exceeded. Please create an account to continue.",
            )
        # Increment their usage count
        current_user.request_count += 1
        await current_user.save()
