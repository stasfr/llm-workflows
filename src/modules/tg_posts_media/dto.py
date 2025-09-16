from uuid import UUID
from pydantic import BaseModel
from typing import Optional


class AddTgPostMedia(BaseModel):
    name: str
    post_id: UUID
    mime_type: Optional[str]


class UpdateTgPostMedia(BaseModel):
    name: str
    post_id: UUID
    mime_type: Optional[str]
