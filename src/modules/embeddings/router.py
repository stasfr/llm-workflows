from typing import Annotated
from fastapi import APIRouter, Body, BackgroundTasks

from src.modules.embeddings.dto import GenerateImageDescriptionsPayload
from src.modules.embeddings.services import start_image_description_generation
from src.schemas import PlainDataResponse, ApiResponse


router = APIRouter(
    prefix="/embeddings",
    tags=["Embeddings"],
)


@router.post("/generate_descriptions", description="Start background job to generate image descriptions")
async def generate_descriptions_handler(
    background_tasks: BackgroundTasks,
    payload: Annotated[GenerateImageDescriptionsPayload, Body()]
) -> ApiResponse[PlainDataResponse]:
    try:
        await start_image_description_generation(payload, background_tasks)
        return ApiResponse(data=PlainDataResponse(message="No errors at start, processing started."))
    except Exception as e:
        return ApiResponse(data=PlainDataResponse(error=str(e)))
