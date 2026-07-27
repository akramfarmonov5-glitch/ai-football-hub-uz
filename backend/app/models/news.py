from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON
from app.core.clock import utcnow
from app.core.database import Base

class News(Base):
    __tablename__ = "news"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    slug = Column(String, unique=True, index=True)
    summary = Column(Text, nullable=True)
    content = Column(Text)
    image_url = Column(String, nullable=True)
    source_url = Column(String, nullable=True)
    tags = Column(JSON, nullable=True)  # list of strings
    is_published = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utcnow, index=True)
