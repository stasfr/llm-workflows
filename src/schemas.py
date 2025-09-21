from typing import Generic, TypeVar, Optional
from pydantic import BaseModel


DataT = TypeVar("DataT")


class ApiResponse(BaseModel, Generic[DataT]):
    data: DataT


class PlainDataResponse(BaseModel):
    message: Optional[str] = None
    error: Optional[str] = None


class DeleteResultResponse(BaseModel):
    deleted: bool
