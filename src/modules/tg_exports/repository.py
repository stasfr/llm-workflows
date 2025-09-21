from typing import Optional
from uuid import UUID

from src.config import (
    DB_USER,
    DB_PASSWORD,
    DB_HOST,
    DB_PORT,
    DB_NAME
)

import psycopg
from psycopg import sql
from psycopg.rows import class_row

from src.modules.tg_exports.schemas import TgExportModel
from src.modules.tg_exports.dto import AddTgExport, UpdateTgExport


class TgExportsRepository:
    @classmethod
    async def get_all(cls) -> list[TgExportModel]:
        async with await psycopg.AsyncConnection.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
        ) as aconn:
            async with aconn.cursor(row_factory=class_row(TgExportModel)) as acur:
                await acur.execute(sql.SQL("""
                    SELECT * FROM tg_exports
                    """))
                tg_export_items = await acur.fetchall()
                return tg_export_items

    @classmethod
    async def add_one(cls, payload: AddTgExport) -> Optional[TgExportModel]:
        async with await psycopg.AsyncConnection.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
        ) as aconn:
            async with aconn.cursor(row_factory=class_row(TgExportModel)) as acur:
                await acur.execute(sql.SQL("""
                      INSERT INTO tg_exports (channel_id, data_path, photos_path)
                      VALUES (%s, %s, %s)
                      RETURNING *
                      """), (payload.channel_id, payload.data_path, payload.photos_path))
                new_tg_export = await acur.fetchone()
                return new_tg_export

    @classmethod
    async def delete(cls, tg_export_id: UUID) -> None:
        async with await psycopg.AsyncConnection.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
        ) as aconn:
            async with aconn.cursor() as acur:
                await acur.execute(sql.SQL("""
                      DELETE FROM tg_exports WHERE id = %s
                      """), (tg_export_id,))

    @classmethod
    async def update(cls, tg_export_id: UUID, payload: UpdateTgExport) -> Optional[TgExportModel]:
        async with await psycopg.AsyncConnection.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
        ) as aconn:
            async with aconn.cursor(row_factory=class_row(TgExportModel)) as acur:
                await acur.execute(sql.SQL("""
                      UPDATE tg_exports
                      SET channel_id = %s, data_path = %s, photos_path = %s
                      WHERE id = %s
                      RETURNING *
                      """), (payload.channel_id, payload.data_path, payload.photos_path, tg_export_id))
                updated_tg_export = await acur.fetchone()
                return updated_tg_export

    @classmethod
    async def get_one_by_id(cls, tg_export_id: UUID) -> Optional[TgExportModel]:
        async with await psycopg.AsyncConnection.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
        ) as aconn:
            async with aconn.cursor(row_factory=class_row(TgExportModel)) as acur:
                await acur.execute(sql.SQL("""
                    SELECT * FROM tg_exports
                    WHERE id = %s
                    """), (tg_export_id,))
                tg_export_item = await acur.fetchone()
                return tg_export_item
