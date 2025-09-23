from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, Body, BackgroundTasks, Path

from src.modules.media_descriptions.dto import GenerateImageDescriptionsPayload
from src.modules.media_descriptions.services import (
    start_image_description_generation_by_export,
)
from src.schemas import PlainDataResponse, ApiResponse


router = APIRouter(
    prefix="/media_descriptions",
    tags=["Media Descriptions"],
)


@router.post(
    "/generate_descriptions/by_tg_export",
    description="Start background job to generate image descriptions for a tg_export",
)
async def generate_descriptions_by_export_handler(
    background_tasks: BackgroundTasks,
    payload: Annotated[GenerateImageDescriptionsPayload, Body()],
) -> ApiResponse[PlainDataResponse]:
    try:
        await start_image_description_generation_by_export(payload, background_tasks)
        return ApiResponse(
            data=PlainDataResponse(
                message="No errors at start, processing started.")
        )
    except Exception as e:
        return ApiResponse(data=PlainDataResponse(error=str(e)))
