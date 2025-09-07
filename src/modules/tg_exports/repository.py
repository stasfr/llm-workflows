from sqlalchemy import select

from src.database import async_session_maker
from src.models import TgExports

from src.modules.tg_exports.schemas import TgExportAdd, TgExport

class TgExportsRepository:
    @classmethod
    async def add_one(cls, payload: TgExportAdd) -> TgExport:
        async with async_session_maker() as session:
            new_tg_export = payload.model_dump()

            tg_export = TgExports(**new_tg_export)
            session.add(tg_export)
            await session.flush()
            await session.commit()

            tg_export_schema = TgExport.model_validate(tg_export)

            return tg_export_schema

    @classmethod
    async def get_all(cls) -> list[TgExport]:
        async with async_session_maker() as session:
            query = select(TgExports)
            result = await session.execute(query)
            tg_exports_models = result.scalars().all()
            tg_exports_schemas = [TgExport.model_validate(tg_export) for tg_export in tg_exports_models]

            return tg_exports_schemas
