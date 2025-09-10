from uuid import UUID
from pydantic import BaseModel


class AddTgExport(BaseModel):
    channel_id: str
    data_path: str
    photos_path: str

class UpdateTgExport(BaseModel):
    id: UUID
    channel_id: str
    data_path: str
    photos_path: str

class DeleteTgExport(BaseModel):
    tg_export_id: UUID
