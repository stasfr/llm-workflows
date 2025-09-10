from pydantic import BaseModel


class CreateDatabasePayload(BaseModel):
    dbname: str

class DeleteDatabasePayload(BaseModel):
    dbname: str

class RecreatePublicSchemaPayload(BaseModel):
    dbname: str

class CreateTablesPayload(BaseModel):
    dbname: str
