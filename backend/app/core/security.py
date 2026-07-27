from datetime import datetime, timedelta
from typing import Optional
from fastapi import Header, HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings


def verify_admin(x_admin_token: Optional[str] = Header(default=None)):
    """FastAPI dependency: guards /admin/* endpoints with a shared admin token."""
    if not x_admin_token or x_admin_token != settings.ADMIN_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Noto'g'ri yoki yo'q admin token (X-Admin-Token).",
        )
    return True

# Since the prompt requires high execution speed, let's make sure we import jose and passlib.
# We will use simple authentication where a static password or admin token is checked for MVP simplicity.
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
