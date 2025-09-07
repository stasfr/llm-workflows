from uuid import UUID
from typing import Annotated, List

from fastapi import APIRouter, Depends

from src.modules.tg_exports.repository import TgExportsRepository
from src.modules.tg_exports.schemas import TgExportAdd, TgExport
from src.schemas import ApiResponse, PlainDataResponse


router = APIRouter(
    prefix="/tg_exports",
    tags=["Telegram Channels Exports"],
)


@router.get('', description="Get all Telegram channels exports for a project.")
async def get_telegram_channels_handler() -> ApiResponse[List[TgExport]] | ApiResponse[PlainDataResponse]:
    try:
        channels = await TgExportsRepository.get_all()
        return ApiResponse(data=channels)
    except Exception as e:
        return ApiResponse(data=PlainDataResponse(error=str(e)))


@router.post('', description="Add a new Telegram channel export.")
async def add_telegram_channel_handler(payload: Annotated[TgExportAdd, Depends()]) -> ApiResponse[TgExport] | ApiResponse[PlainDataResponse]:
    try:
        channel = await TgExportsRepository.add_one(payload)
        return ApiResponse(data=channel)
    except Exception as e:
        return ApiResponse(data=PlainDataResponse(error=str(e)))

@router.get('/{id}', description="Get a Telegram channel export by ID.")
async def get_telegram_channel_handler(id: UUID) -> ApiResponse[TgExport] | ApiResponse[PlainDataResponse]:
    try:
        channel = await TgExportsRepository.get_one_by_id(id)

        if not channel:
            return ApiResponse(data=PlainDataResponse(error=f"Telegram channel export with ID {id} not found"))

        return ApiResponse(data=channel)
    except Exception as e:
        return ApiResponse(data=PlainDataResponse(error=str(e)))
