from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, Body, BackgroundTasks, Path

from src.modules.embeddings.dto import GenerateImageDescriptionsPayload
from src.modules.embeddings.services import (
    start_image_description_generation_by_export,
    start_image_description_generation_by_post,
    start_image_description_generation_by_media,
)
from src.schemas import PlainDataResponse, ApiResponse


router = APIRouter(
    prefix="/embeddings",
    tags=["Embeddings"],
)


@router.post(
    "/generate_descriptions/by_tg_export/{tg_export_id}",
    description="Start background job to generate image descriptions for a tg_export",
)
async def generate_descriptions_by_export_handler(
    background_tasks: BackgroundTasks,
    tg_export_id: Annotated[UUID, Path(description="ID of the tg_export")],
    payload: Annotated[GenerateImageDescriptionsPayload, Body()],
) -> ApiResponse[PlainDataResponse]:
    try:
        await start_image_description_generation_by_export(
            tg_export_id, payload, background_tasks
        )
        return ApiResponse(
            data=PlainDataResponse(message="No errors at start, processing started.")
        )
    except Exception as e:
        return ApiResponse(data=PlainDataResponse(error=str(e)))


@router.post(
    "/generate_descriptions/by_tg_post/{tg_post_id}",
    description="Start background job to generate image descriptions for a tg_post",
)
async def generate_descriptions_by_post_handler(
    background_tasks: BackgroundTasks,
    tg_post_id: Annotated[UUID, Path(description="ID of the tg_post")],
    payload: Annotated[GenerateImageDescriptionsPayload, Body()],
) -> ApiResponse[PlainDataResponse]:
    try:
        await start_image_description_generation_by_post(
            tg_post_id, payload, background_tasks
        )
        return ApiResponse(
            data=PlainDataResponse(message="No errors at start, processing started.")
        )
    except Exception as e:
        return ApiResponse(data=PlainDataResponse(error=str(e)))


@router.post(
    "/generate_descriptions/by_media/{tg_media_id}",
    description="Start background job to generate image descriptions for a media",
)
async def generate_descriptions_by_media_handler(
    background_tasks: BackgroundTasks,
    tg_media_id: Annotated[UUID, Path(description="ID of the media")],
    payload: Annotated[GenerateImageDescriptionsPayload, Body()],
) -> ApiResponse[PlainDataResponse]:
    try:
        await start_image_description_generation_by_media(
            tg_media_id, payload, background_tasks
        )
        return ApiResponse(
            data=PlainDataResponse(message="No errors at start, processing started.")
        )
    except Exception as e:
        return ApiResponse(data=PlainDataResponse(error=str(e)))
