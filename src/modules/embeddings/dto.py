from typing import Optional
from uuid import UUID
from pydantic import BaseModel, model_validator


class GenerateImageDescriptionsPayload(BaseModel):
    tg_export_id: Optional[UUID] = None
    tg_post_id: Optional[UUID] = None
    tg_media_id: Optional[UUID] = None
    model_name: str = "llava-1.5-7b-hf"

    @model_validator(mode='after')
    def validate_ids(self) -> 'GenerateImageDescriptionsPayload':
        if sum(id is not None for id in [self.tg_export_id, self.tg_post_id, self.tg_media_id]) != 1:
            raise ValueError("Exactly one of tg_export_id, tg_post_id, or tg_media_id must be provided.")
        return self
