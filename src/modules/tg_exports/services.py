from typing import List
from uuid import UUID

from src.modules.tg_exports.repository import TgExportsRepository
from src.modules.tg_exports.schemas import TgExportModel
from src.modules.tg_exports.dto import AddTgExport, UpdateTgExport


async def get_all_telegram_exports() -> List[TgExportModel]:
    all_tg_exports = await TgExportsRepository.get_all()
    return all_tg_exports


async def add_telegram_export(payload: AddTgExport) -> TgExportModel:
    new_tg_export = await TgExportsRepository.add_one(payload)

    if not new_tg_export:
        raise ValueError("Failed to create Telegram export")

    return new_tg_export


async def delete_telegram_export(tg_export_id: UUID) -> None:
    await TgExportsRepository.delete(tg_export_id)


async def update_telegram_export(tg_export_id: UUID, payload: UpdateTgExport) -> TgExportModel:
    updated_tg_export = await TgExportsRepository.update(tg_export_id, payload)

    if not updated_tg_export:
        raise ValueError("Failed to update Telegram export")

    return updated_tg_export


async def get_telegram_export(tg_export_id: UUID) -> TgExportModel:
    tg_export_item = await TgExportsRepository.get_one_by_id(tg_export_id)

    if not tg_export_item:
        raise ValueError("Telegram export not found")

    return tg_export_item
