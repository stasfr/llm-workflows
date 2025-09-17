from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, Body, BackgroundTasks, Path

from src.modules.embeddings.dto import GeneratePostEmbeddingsPayload
from src.modules.embeddings.services import start_post_embedding_generation_by_export
from src.schemas import PlainDataResponse, ApiResponse


router = APIRouter(
    prefix="/post_embeddings",
    tags=["Post Embeddings"],
)


@router.post(
    "/generate_embeddings/by_tg_export/{tg_export_id}",
    description="Start background job to generate embeddings for all posts in a tg_export",
)
async def generate_embeddings_by_export_handler(
    background_tasks: BackgroundTasks,
    tg_export_id: Annotated[UUID, Path(description="ID of the tg_export")],
    payload: Annotated[GeneratePostEmbeddingsPayload, Body()],
) -> ApiResponse[PlainDataResponse]:
    try:
        await start_post_embedding_generation_by_export(
            tg_export_id, payload, background_tasks
        )
        return ApiResponse(
            data=PlainDataResponse(message="No errors at start, processing started.")
        )
    except Exception as e:
        return ApiResponse(data=PlainDataResponse(error=str(e)))
