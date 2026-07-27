from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional, List

from app.core.clock import as_utc

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

    @field_validator("created_at")
    @classmethod
    def _mark_as_utc(cls, value: datetime) -> datetime:
        """Naive UTC -> timezone'li UTC (clock.py dagi kelishuvga qarang)."""
        return as_utc(value)

    class Config:
        from_attributes = True
