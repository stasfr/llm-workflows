import json
from typing import List, Optional
from uuid import UUID
from src.config import DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME
import psycopg
from psycopg import sql
from psycopg.rows import dict_row

class EmbeddingsRepository:
    @classmethod
    async def get_media_for_processing_by_export_id(cls, export_id: UUID, limit: int, offset: int) -> List[dict]:
        async with await psycopg.AsyncConnection.connect(
            user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT, dbname=DB_NAME
        ) as aconn:
            async with aconn.cursor(row_factory=dict_row) as acur:
                await acur.execute(sql.SQL("""
                    SELECT m.id as media_id, m.name as media_name, te.photos_path
                    FROM medias m
                    JOIN posts p ON m.post_id = p.id
                    JOIN tg_exports te ON p.from_id = te.id
                    LEFT JOIN media_datas md ON m.id = md.media_id
                    WHERE te.id = %s AND m.mime_type LIKE 'image/%%' AND (md.id IS NULL OR md.description IS NULL)
                    LIMIT %s OFFSET %s
                """), (export_id, limit, offset))
                return await acur.fetchall()

    @classmethod
    async def get_media_for_processing_by_post_id(cls, post_id: UUID, limit: int, offset: int) -> List[dict]:
        async with await psycopg.AsyncConnection.connect(
            user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT, dbname=DB_NAME
        ) as aconn:
            async with aconn.cursor(row_factory=dict_row) as acur:
                await acur.execute(sql.SQL("""
                    SELECT m.id as media_id, m.name as media_name, te.photos_path
                    FROM medias m
                    JOIN posts p ON m.post_id = p.id
                    JOIN tg_exports te ON p.from_id = te.id
                    LEFT JOIN media_datas md ON m.id = md.media_id
                    WHERE p.id = %s AND m.mime_type LIKE 'image/%%' AND (md.id IS NULL OR md.description IS NULL)
                    LIMIT %s OFFSET %s
                """), (post_id, limit, offset))
                return await acur.fetchall()

    @classmethod
    async def get_media_for_processing_by_media_id(cls, media_id: UUID) -> Optional[dict]:
         async with await psycopg.AsyncConnection.connect(
            user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT, dbname=DB_NAME
        ) as aconn:
            async with aconn.cursor(row_factory=dict_row) as acur:
                await acur.execute(sql.SQL("""
                    SELECT m.id as media_id, m.name as media_name, te.photos_path
                    FROM medias m
                    JOIN posts p ON m.post_id = p.id
                    JOIN tg_exports te ON p.from_id = te.id
                    LEFT JOIN media_datas md ON m.id = md.media_id
                    WHERE m.id = %s AND m.mime_type LIKE 'image/%%' AND (md.id IS NULL OR md.description IS NULL)
                """), (media_id,))
                return await acur.fetchone()

    @classmethod
    async def update_media_data(cls, media_id: UUID, description: str, tag: str, structured_description: str,
                                desc_usage: Optional[dict], tag_usage: Optional[dict], struct_desc_usage: Optional[dict],
                                desc_time: float, tag_time: float, struct_desc_time: float) -> None:
        async with await psycopg.AsyncConnection.connect(
            user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT, dbname=DB_NAME
        ) as aconn:
            async with aconn.cursor() as acur:
                await acur.execute(sql.SQL("""
                    UPDATE media_datas
                    SET
                        description = %s,
                        tag = %s,
                        structured_description = %s,
                        description_usage = %s,
                        tag_usage = %s,
                        structured_description_usage = %s,
                        description_time = %s,
                        tag_time = %s,
                        structured_description_time = %s
                    WHERE media_id = %s
                """), (
                    description, tag, structured_description,
                    json.dumps(desc_usage) if desc_usage else None,
                    json.dumps(tag_usage) if tag_usage else None,
                    json.dumps(struct_desc_usage) if struct_desc_usage else None,
                    desc_time, tag_time, struct_desc_time,
                    media_id
                ))
