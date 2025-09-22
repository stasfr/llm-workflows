from pydantic import BaseModel, ConfigDict
from datetime import datetime
from uuid import UUID
from typing import Optional, Dict, Any


class ExperimentModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tg_export_id: Optional[UUID]
    milvus_collection_name: str
    meta_data: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: Optional[datetime]
