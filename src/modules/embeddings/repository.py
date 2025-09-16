import json
from typing import List, Optional
from uuid import UUID
from src.config import DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME
import psycopg
from psycopg import sql
from psycopg.rows import dict_row

from src.modules.embeddings.schemas import MediaForProcessing, MediaDataUpdate


class EmbeddingsRepository:
    @classmethod
    async def get_media_for_processing_by_export_id(cls, export_id: UUID, limit: int, offset: int) -> List[MediaForProcessing]:
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
                    ORDER BY m.id
                    LIMIT %s OFFSET %s
                """), (export_id, limit, offset))
                result = await acur.fetchall()
                return [MediaForProcessing(**row) for row in result]

    @classmethod
    async def get_media_for_processing_by_post_id(cls, post_id: UUID, limit: int, offset: int) -> List[MediaForProcessing]:
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
                    ORDER BY m.id
                    LIMIT %s OFFSET %s
                """), (post_id, limit, offset))
                result = await acur.fetchall()
                return [MediaForProcessing(**row) for row in result]

    @classmethod
    async def get_media_for_processing_by_media_id(cls, media_id: UUID) -> Optional[MediaForProcessing]:
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
                result = await acur.fetchone()
                return MediaForProcessing(**result) if result else None

    @classmethod
    async def update_media_data(cls, data: MediaDataUpdate) -> None:
        async with await psycopg.AsyncConnection.connect(
            user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT, dbname=DB_NAME
        ) as aconn:
            async with aconn.cursor() as acur:
                await acur.execute(sql.SQL("""
                    INSERT INTO media_datas (
                        media_id, description, tag, structured_description,
                        description_usage, tag_usage, structured_description_usage,
                        description_time, tag_time, structured_description_time
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (media_id) DO UPDATE SET
                        description = EXCLUDED.description,
                        tag = EXCLUDED.tag,
                        structured_description = EXCLUDED.structured_description,
                        description_usage = EXCLUDED.description_usage,
                        tag_usage = EXCLUDED.tag_usage,
                        structured_description_usage = EXCLUDED.structured_description_usage,
                        description_time = EXCLUDED.description_time,
                        tag_time = EXCLUDED.tag_time,
                        structured_description_time = EXCLUDED.structured_description_time
                """), (
                    data.media_id,
                    data.description,
                    data.tag,
                    data.structured_description,
                    json.dumps(data.desc_usage) if data.desc_usage else None,
                    json.dumps(data.tag_usage) if data.tag_usage else None,
                    json.dumps(data.struct_desc_usage) if data.struct_desc_usage else None,
                    data.desc_time,
                    data.tag_time,
                    data.struct_desc_time,
                ))
