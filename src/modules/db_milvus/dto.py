from pydantic import BaseModel, Field


class CreateCollectionPayload(BaseModel):
    collection_name: str
    dim: int = Field(..., gt=0,
                     description="Dimension of the vector embeddings")


class DeleteCollectionPayload(BaseModel):
    collection_name: str
