from sqlalchemy import Column, Integer, String, DateTime, func
from datetime import datetime, timedelta
from app.database import Base

class WebURL(Base):
    __tablename__ = "web_urls"

    id = Column(Integer, primary_key=True, index=True)
    original_url = Column(String, index=True)
    suffix       = Column(String, unique=True, index=True)
    clicks       = Column(Integer, default=0)
    created_at   = Column(DateTime, default=func.now())
    expires_at   = Column(DateTime, default=lambda: datetime.now() + timedelta(days=3))