from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from src.pkg.telegram_schemas import Reactions


class StartParsing(BaseModel):
    apply_filters: bool

class CreateMedia(BaseModel):
    name: str
    mime_type: Optional[str]

class CreatePost(BaseModel):
    post_id: int
    date: Optional[datetime]
    edited: Optional[datetime]
    post_text: Optional[str]
    reactions: Optional[List[Reactions]]
    media: List[CreateMedia]
