from pydantic import BaseModel


class GenerateImageDescriptionsPayload(BaseModel):
    model_name: str = "google/gemma-3-4b"
