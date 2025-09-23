from typing import Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel


class MediaForProcessing(BaseModel):
    media_id: UUID
    media_data_id: UUID
    media_name: str


class MediaDataUpdate(BaseModel):
    media_data_id: UUID
    media_id: UUID
    description: str
    tag: str
    structured_description: str
    desc_usage: Optional[Dict[str, Any]]
    tag_usage: Optional[Dict[str, Any]]
    struct_desc_usage: Optional[Dict[str, Any]]
    desc_time: float
    tag_time: float
    struct_desc_time: float
