from uuid import UUID
from typing import List, Annotated

from fastapi import APIRouter, Body, Path

from src.modules.tg_exports.services import get_all_telegram_exports, add_telegram_export, update_telegram_export, delete_telegram_export, get_telegram_export
from src.modules.tg_exports.schemas import TgExportModel
from src.modules.tg_exports.dto import AddTgExport, DeleteTgExport, UpdateTgExport
from src.schemas import PlainDataResponse, ApiResponse


router = APIRouter(
    prefix="/tg_exports",
    tags=["Telegram Channels Exports"],
)


@router.get("/", description="Get all Telegram channels exports.")
async def get_all_telegram_exports_handler() -> ApiResponse[List[TgExportModel] | PlainDataResponse]:
    try:
        all_tg_exports = await get_all_telegram_exports()
        return ApiResponse(data=all_tg_exports)
    except Exception as e:
        return ApiResponse(data=PlainDataResponse(error=str(e)))


@router.post("/", description="Add a new Telegram channel export.")
async def add_telegram_export_handler(
    payload: Annotated[AddTgExport, Body(description="Telegram channel export creation payload")]
) -> ApiResponse[TgExportModel] | ApiResponse[PlainDataResponse]:
    try:
        new_tg_export = await add_telegram_export(payload)
        return ApiResponse(data=new_tg_export)
    except Exception as e:
        return ApiResponse(data=PlainDataResponse(error=str(e)))


@router.post("/test_channel", description="Add a new Telegram channel export.")
async def add_test_telegram_export_handler() -> ApiResponse[TgExportModel] | ApiResponse[PlainDataResponse]:
    try:
        test_payload = AddTgExport(
            channel_id="channel1510200344",
            data_path="\\instajeldor\\test",
            photos_path="\\instajeldor\\photos",
        )
        new_tg_export = await add_telegram_export(test_payload)
        return ApiResponse(data=new_tg_export)
    except Exception as e:
        return ApiResponse(data=PlainDataResponse(error=str(e)))


@router.delete("/{tg_export_id}", description="Delete a Telegram channel export.")
async def delete_telegram_export_handler(
    tg_export_id: Annotated[UUID, Path(
        title="Id of Telegram export (UUID v4)",
        description="Id of the Telegram export to be deleted",
        examples=["3fa85f64-5717-4562-b3fc-2c963f66afa6"]
    )]
) -> ApiResponse[PlainDataResponse]:
    try:
        await delete_telegram_export(tg_export_id)
        return ApiResponse(data=PlainDataResponse(message="Done!"))
    except Exception as e:
        return ApiResponse(data=PlainDataResponse(error=str(e)))


@router.put("/{tg_export_id}", description="Update a Telegram channel export.")
async def update_telegram_export_handler(
    tg_export_id: Annotated[UUID, Path(
        title="Id of Telegram export (UUID v4)",
        description="Id of the Telegram export to be deleted",
        examples=["3fa85f64-5717-4562-b3fc-2c963f66afa6"]
    )],
    payload: Annotated[UpdateTgExport, Body(description="Telegram channel export creation payload")]
) -> ApiResponse[TgExportModel] | ApiResponse[PlainDataResponse]:
    try:
        updated_tg_export = await update_telegram_export(tg_export_id, payload)
        return ApiResponse(data=updated_tg_export)
    except Exception as e:
        return ApiResponse(data=PlainDataResponse(error=str(e)))


@router.get("/{tg_export_id}", description="Get a Telegram export by ID.")
async def get_telegram_export_handler(
    tg_export_id: Annotated[UUID, Path(
        title="Id of Telegram export (UUID v4)",
        description="Id of the Telegram export to be deleted",
        examples=["3fa85f64-5717-4562-b3fc-2c963f66afa6"]
    )]
) -> ApiResponse[TgExportModel | PlainDataResponse]:
    try:
        tg_export_item = await get_telegram_export(tg_export_id)
        return ApiResponse(data=tg_export_item)
    except Exception as e:
        return ApiResponse(data=PlainDataResponse(error=str(e)))
