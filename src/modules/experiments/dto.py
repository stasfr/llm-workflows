from uuid import UUID
from pydantic import BaseModel
from typing import Optional, Dict, Any


class AddExperiment(BaseModel):
    tg_export_id: Optional[UUID]
    sqlite_path: str
    milvus_collection_name: str
    meta_data: Optional[Dict[str, Any]] = None


class UpdateExperiment(BaseModel):
    tg_export_id: Optional[UUID]
    sqlite_path: str
    milvus_collection_name: str
    meta_data: Optional[Dict[str, Any]] = None


class DeleteExperiment(BaseModel):
    experiment_id: UUID
