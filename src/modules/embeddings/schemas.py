from typing import Optional, List
from pydantic import BaseModel
from uuid import UUID


class PostForEmbedding(BaseModel):
    post_id: UUID
    post_text: Optional[str] = None
    photos_path: str


class PostMediaForEmbedding(BaseModel):
    media_id: UUID
    media_name: str
    description: Optional[str] = None
