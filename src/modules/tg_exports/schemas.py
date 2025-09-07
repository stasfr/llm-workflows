from pydantic import BaseModel, ConfigDict
from datetime import datetime
from uuid import UUID


class TgExportAdd(BaseModel):
    channel_id: str
    data_path: str
    photos_path: str

class TgExport(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    channel_id: str
    data_path: str
    photos_path: str
    created_at: datetime
