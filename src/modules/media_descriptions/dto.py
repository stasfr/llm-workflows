from uuid import UUID
from pydantic import BaseModel


class GenerateImageDescriptionsPayload(BaseModel):
    tg_export_id: UUID
    experiment_id: UUID
    model_name: str = "google/gemma-3-4b"
