from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class NewsBase(BaseModel):
    title: str
    summary: Optional[str] = None
    content: str
    image_url: Optional[str] = None
    source_url: Optional[str] = None
    tags: Optional[List[str]] = None
    is_published: bool = True

class NewsCreate(NewsBase):
    pass

class NewsUpdate(BaseModel):
    title: Optional[str] = None
    summary: Optional[str] = None
    content: Optional[str] = None
    image_url: Optional[str] = None
    source_url: Optional[str] = None
    tags: Optional[List[str]] = None
    is_published: Optional[bool] = None

class NewsResponse(NewsBase):
    id: int
    slug: str
    created_at: datetime

    class Config:
        from_attributes = True
