from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from uuid import UUID
from src.pkg.telegram_schemas import Reactions


class TgPostModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    post_id: int
    date: Optional[datetime]
    edited: Optional[datetime]
    post_text: Optional[str]
    reactions: Optional[List[Reactions]]
    from_id: Optional[UUID]
    created_at: datetime
