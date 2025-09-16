from uuid import UUID
from pydantic import BaseModel
from typing import Optional, Dict

class AddTgPostsMediaData(BaseModel):
    media_id: UUID
    description: Optional[str] = None
    tag: Optional[str] = None
    structured_description: Optional[str] = None
    description_usage: Optional[Dict] = None
    tag_usage: Optional[Dict] = None
    structured_description_usage: Optional[Dict] = None
    description_time: Optional[float] = None
    tag_time: Optional[float] = None
    structured_description_time: Optional[float] = None


class UpdateTgPostsMediaData(BaseModel):
    media_id: UUID
    description: Optional[str] = None
    tag: Optional[str] = None
    structured_description: Optional[str] = None
    description_usage: Optional[Dict] = None
    tag_usage: Optional[Dict] = None
    structured_description_usage: Optional[Dict] = None
    description_time: Optional[float] = None
    tag_time: Optional[float] = None
    structured_description_time: Optional[float] = None
