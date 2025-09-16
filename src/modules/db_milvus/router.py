from fastapi import APIRouter, Body

from src.schemas import ApiResponse, PlainDataResponse
from src.modules.db_milvus.services import (
    create_new_collection,
    delete_collection,
    get_collection_list,
)
from src.modules.db_milvus.dto import CreateCollectionPayload, DeleteCollectionPayload

router = APIRouter(
    prefix="/db_milvus",
    tags=["Milvus Collection Operations"],
)


@router.get("/collections", description="Get all collection names in Milvus")
def get_collection_list_handler() -> ApiResponse[list[str] | PlainDataResponse]:
    try:
        collections = get_collection_list()
        return ApiResponse(data=collections)
    except Exception as e:
        return ApiResponse(data=PlainDataResponse(error=str(e)))

@router.post("/create_collection", description="Create a new collection in Milvus")
def create_new_collection_handler(
    payload: CreateCollectionPayload = Body(...)
) -> ApiResponse[PlainDataResponse]:
    try:
        create_new_collection(payload.collection_name, payload.dim)
        return ApiResponse(data=PlainDataResponse(message=f"Collection '{payload.collection_name}' created successfully."))
    except Exception as e:
        return ApiResponse(data=PlainDataResponse(error=str(e)))

@router.delete("/delete_collection", description="Delete a collection in Milvus")
def delete_collection_handler(
    payload: DeleteCollectionPayload = Body(...)
) -> ApiResponse[PlainDataResponse]:
    try:
        delete_collection(payload.collection_name)
        return ApiResponse(data=PlainDataResponse(message=f"Collection '{payload.collection_name}' deleted successfully."))
    except Exception as e:
        return ApiResponse(data=PlainDataResponse(error=str(e)))
