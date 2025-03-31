from pydantic import BaseModel, HttpUrl
from datetime import datetime
from typing import Optional

class WebURLBase(BaseModel):
    original_url: HttpUrl

class WebURLCreate(WebURLBase):
    custom_suffix: Optional[str] = None

class WebURLRead(WebURLBase):
    id: int
    suffix: str
    clicks: int
    created_at: datetime
    expires_at: datetime

    class ConfigDict:
        from_attributes = True

class WebURLResponse(BaseModel):
    short_url: str
    original_url: str
    expires_at: datetime