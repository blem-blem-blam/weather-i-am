# In a file like app/security.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from jose import JWTError, jwt
from pydantic import BaseModel
import uuid
from datetime import datetime, timedelta

from app.models.user_model import Users

# --- Configuration (keep these in a .env file) ---
SECRET_KEY = "your-super-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 30  # 30 days for anonymous tokens


# Pydantic model for the token payload
class TokenData(BaseModel):
    sub: str  # This will be the user's ID as a string
    scopes: list[str] = []


# Reusable security scheme
oauth2_scheme = HTTPBearer(auto_error=False)


# --- Token Creation ---
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        # A default short expiry for regular users
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# --- THE CORE DEPENDENCY ---
async def get_current_user(
    token_wrapper: HTTPBearer = Depends(oauth2_scheme),
) -> Users | None:
    if token_wrapper is None:
        # No 'Authorization' header was provided at all
        return None

    token = token_wrapper.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id_str: str = payload.get("sub")
        if user_id_str is None:
            raise credentials_exception
        token_data = TokenData(sub=user_id_str)
    except JWTError:
        raise credentials_exception

    # Fetch the user from the database
    user = await Users.get(uuid.UUID(token_data.sub))
    if user is None:
        raise credentials_exception
    return user
