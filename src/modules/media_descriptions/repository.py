import json
from typing import List, Optional
from uuid import UUID
from src.config import DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME
import psycopg
from psycopg import sql
from psycopg.rows import dict_row

from src.modules.media_descriptions.schemas import MediaForProcessing, MediaDataUpdate


class MediaDescriptionsRepository:
    @classmethod
    async def get_media_for_processing_by_export_id(cls, export_id: UUID, limit: int, offset: int) -> List[MediaForProcessing]:
        async with await psycopg.AsyncConnection.connect(
            user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT, dbname=DB_NAME
        ) as aconn:
            async with aconn.cursor(row_factory=dict_row) as acur:
                await acur.execute(sql.SQL("""
                    SELECT m.id as media_id, md.id as media_data_id, m.name as media_name, te.photos_path
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
                    SELECT m.id as media_id, md.id as media_data_id, m.name as media_name, te.photos_path
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
                    SELECT m.id as media_id, md.id as media_data_id, m.name as media_name, te.photos_path
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
                    UPDATE media_datas
                    SET media_id = %s, description = %s, tag = %s, structured_description = %s, description_usage = %s, tag_usage = %s, structured_description_usage = %s, description_time = %s, tag_time = %s, structured_description_time = %s
                    WHERE id = %s
                    RETURNING *
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
                    data.media_data_id,
                ))
