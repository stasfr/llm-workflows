from typing import Optional
from uuid import UUID

from sqlalchemy import delete, select, update

from src.database import async_session_maker
from src.models import TgExportsModel

from src.modules.tg_exports.schemas import TgExport, TgExportAdd

class TgExportsRepository:
    @classmethod
    async def add_one(cls, payload: TgExportAdd) -> TgExport:
        async with async_session_maker() as session:
            new_tg_export = payload.model_dump()

            tg_export = TgExportsModel(**new_tg_export)
            session.add(tg_export)
            await session.flush()
            await session.commit()

            tg_export_schema = TgExport.model_validate(tg_export)

            return tg_export_schema

    @classmethod
    async def get_all(cls) -> list[TgExport]:
        async with async_session_maker() as session:
            query = select(TgExportsModel)
            result = await session.execute(query)
            tg_exports_models = result.scalars().all()
            tg_exports_schemas = [
                TgExport.model_validate(tg_export) for tg_export in tg_exports_models
            ]

            return tg_exports_schemas

    @classmethod
    async def get_one_by_id(cls, tg_export_id: UUID) -> Optional[TgExport]:
        async with async_session_maker() as session:
            query = select(TgExportsModel).where(TgExportsModel.id == tg_export_id)
            result = await session.execute(query)
            tg_export_model = result.scalar_one_or_none()

            if tg_export_model is None:
                return None

            tg_export_schema = TgExport.model_validate(tg_export_model)

            return tg_export_schema

    @classmethod
    async def update_one_by_id(
        cls, tg_export_id: UUID, payload: TgExportAdd
    ) -> Optional[TgExport]:
        async with async_session_maker() as session:
            update_data = payload.model_dump()

            query = (
                update(TgExportsModel)
                .where(TgExportsModel.id == tg_export_id)
                .values(**update_data)
                .returning(TgExportsModel)
            )
            result = await session.execute(query)
            await session.commit()
            updated_tg_export_model = result.scalar_one_or_none()

            if updated_tg_export_model is None:
                return None

            tg_export_schema = TgExport.model_validate(updated_tg_export_model)

            return tg_export_schema

    @classmethod
    async def delete_one_by_id(cls, tg_export_id: UUID) -> bool:
        async with async_session_maker() as session:
            query = delete(TgExportsModel).where(TgExportsModel.id == tg_export_id)
            result = await session.execute(query)
            await session.commit()
            return result.rowcount > 0
