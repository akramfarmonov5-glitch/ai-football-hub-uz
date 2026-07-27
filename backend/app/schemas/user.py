from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    telegram_id: Optional[str] = None
    username: Optional[str] = None
    favorite_team: Optional[str] = None
    is_admin: bool = False

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
        
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
