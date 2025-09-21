from typing import Optional, Dict
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from uuid import UUID


class TgPostsMediaDataModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
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
    created_at: datetime
