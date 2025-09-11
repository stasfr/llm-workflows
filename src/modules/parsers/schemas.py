from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from uuid import UUID
from src.pkg.telegram_schemas import Reactions


class PostModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID

    post_id: int
    date: Optional[datetime]
    edited: Optional[datetime]
    post_text: Optional[str]
    reactions: Optional[List[Reactions]]

    from_id: Optional[UUID]

    created_at: datetime

class MediaModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID

    name: str
    mime_type: str

    post_id: Optional[UUID]

    created_at: datetime

class MediaDataModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID

    description: Optional[str]
    tag: Optional[str]
    structured_description: Optional[dict]
    description_usage: Optional[dict]
    tag_usage: Optional[dict]
    structured_description_usage: Optional[dict]
    description_time: Optional[float]
    tag_time: Optional[float]
    structured_description_time: Optional[float]

    media_id: Optional[UUID]

    created_at: datetime
