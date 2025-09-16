from uuid import UUID
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from src.pkg.telegram_schemas import Reactions


class AddTgPost(BaseModel):
    post_id: int
    from_id: UUID
    date: Optional[datetime] = None
    edited: Optional[datetime] = None
    post_text: Optional[str] = None
    reactions: Optional[List[Reactions]] = None


class UpdateTgPost(BaseModel):
    post_id: int
    from_id: UUID
    date: Optional[datetime] = None
    edited: Optional[datetime] = None
    post_text: Optional[str] = None
    reactions: Optional[List[Reactions]] = None
