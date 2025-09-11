from typing import List, Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel


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
    reactions: Optional[List[dict]]
    media: List[CreateMedia]
