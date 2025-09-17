from pydantic import BaseModel
from uuid import UUID


class GeneratePostEmbeddingsPayload(BaseModel):
    model_name: str = "text-embedding-intfloat-multilingual-e5-large-instruct"
