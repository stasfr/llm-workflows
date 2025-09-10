from pydantic import BaseModel


class CreateDatabasePayload(BaseModel):
    dbname: str

class DeleteDatabasePayload(BaseModel):
    dbname: str
