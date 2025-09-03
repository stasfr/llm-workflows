from pydantic import BaseModel
from typing import Optional

class ParsedTelegramData(BaseModel):
    id: int
    date: str
    text: Optional[str] = None
    photo: Optional[str] = None
