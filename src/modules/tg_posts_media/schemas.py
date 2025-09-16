from typing import Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from uuid import UUID


class TgPostMediaModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    post_id: UUID
    mime_type: Optional[str]
    created_at: datetime
