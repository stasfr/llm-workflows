from typing import List, Optional
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel
from src.pkg.telegram_schemas import Reactions


class StartParsing(BaseModel):
    apply_filters: bool
    tg_export_id: UUID
    experiment_id: UUID


class CreateMedia(BaseModel):
    name: str
    mime_type: Optional[str]


class CreatePost(BaseModel):
    post_id: int
    date: Optional[datetime]
    edited: Optional[datetime]
    post_text: Optional[str]
    reactions: Optional[List[Reactions]]
    has_media: bool
    media: List[CreateMedia]
