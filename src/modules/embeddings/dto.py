from typing import Optional
from uuid import UUID
from pydantic import BaseModel, field_validator

class GenerateImageDescriptionsPayload(BaseModel):
    tg_export_id: Optional[UUID] = None
    tg_post_id: Optional[UUID] = None
    tg_media_id: Optional[UUID] = None
    model_name: str = "llava-1.5-7b-hf"

    @field_validator("tg_export_id", "tg_post_id", "tg_media_id")
    def validate_ids(cls, values):
        ids = [values.get('tg_export_id'), values.get('tg_post_id'), values.get('tg_media_id')]
        if sum(id is not None for id in ids) != 1:
            raise ValueError("Exactly one of tg_export_id, tg_post_id, or tg_media_id must be provided.")
        return values
