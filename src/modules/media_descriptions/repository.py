import json
import os
from typing import List, Optional
from uuid import UUID

import aiosqlite

from src.config import STORAGE_FOLDER
from src.modules.media_descriptions.schemas import MediaForProcessing, MediaDataUpdate


class MediaDescriptionsRepository:
    @classmethod
    async def _get_db_path(cls, experiment_id: UUID) -> str:
        return os.path.join(STORAGE_FOLDER, str(experiment_id), "dataset.db")

    @classmethod
    async def get_media_for_processing_by_export_id(cls, experiment_id: UUID, export_id: UUID, limit: int, offset: int) -> List[MediaForProcessing]:
        db_path = await cls._get_db_path(experiment_id)
        async with aiosqlite.connect(db_path) as db:
            cursor = await db.execute(
                """
                SELECT m.id as media_id, md.id as media_data_id, m.name as media_name
                FROM medias m
                JOIN posts p ON m.post_id = p.id
                LEFT JOIN media_datas md ON m.id = md.media_id
                WHERE p.from_id = ? AND (m.mime_type LIKE 'image/%') AND (md.id IS NULL OR md.description IS NULL)
                ORDER BY m.id
                LIMIT ? OFFSET ?
                """,
                (str(export_id), limit, offset),
            )
            rows = await cursor.fetchall()
            return [MediaForProcessing(media_id=UUID(r[0]), media_data_id=UUID(r[1]) if r[1] else UUID(int=0), media_name=r[2]) for r in rows]

    @classmethod
    async def get_media_for_processing_by_post_id(cls, experiment_id: UUID, post_id: UUID, limit: int, offset: int) -> List[MediaForProcessing]:
        db_path = await cls._get_db_path(experiment_id)
        async with aiosqlite.connect(db_path) as db:
            cursor = await db.execute(
                """
                SELECT m.id as media_id, md.id as media_data_id, m.name as media_name
                FROM medias m
                JOIN posts p ON m.post_id = p.id
                LEFT JOIN media_datas md ON m.id = md.media_id
                WHERE p.id = ? AND (m.mime_type LIKE 'image/%') AND (md.id IS NULL OR md.description IS NULL)
                ORDER BY m.id
                LIMIT ? OFFSET ?
                """,
                (str(post_id), limit, offset),
            )
            rows = await cursor.fetchall()
            return [MediaForProcessing(media_id=UUID(r[0]), media_data_id=UUID(r[1]) if r[1] else UUID(int=0), media_name=r[2]) for r in rows]

    @classmethod
    async def get_media_for_processing_by_media_id(cls, experiment_id: UUID, media_id: UUID) -> Optional[MediaForProcessing]:
        db_path = await cls._get_db_path(experiment_id)
        async with aiosqlite.connect(db_path) as db:
            cursor = await db.execute(
                """
                SELECT m.id as media_id, md.id as media_data_id, m.name as media_name
                FROM medias m
                LEFT JOIN media_datas md ON m.id = md.media_id
                WHERE m.id = ? AND (m.mime_type LIKE 'image/%') AND (md.id IS NULL OR md.description IS NULL)
                """,
                (str(media_id),),
            )
            row = await cursor.fetchone()
            if row:
                return MediaForProcessing(media_id=UUID(row[0]), media_data_id=UUID(row[1]) if row[1] else UUID(int=0), media_name=row[2])
            return None

    @classmethod
    async def update_media_data(cls, experiment_id: UUID, data: MediaDataUpdate) -> None:
        db_path = await cls._get_db_path(experiment_id)
        async with aiosqlite.connect(db_path) as db:
            await db.execute(
                """
                UPDATE media_datas
                SET media_id = ?, description = ?, tag = ?, structured_description = ?, description_usage = ?, tag_usage = ?, structured_description_usage = ?, description_time = ?, tag_time = ?, structured_description_time = ?
                WHERE id = ?
                """,
                (
                    str(data.media_id),
                    data.description,
                    data.tag,
                    data.structured_description,
                    json.dumps(data.desc_usage) if data.desc_usage else None,
                    json.dumps(data.tag_usage) if data.tag_usage else None,
                    json.dumps(
                        data.struct_desc_usage) if data.struct_desc_usage else None,
                    data.desc_time,
                    data.tag_time,
                    data.struct_desc_time,
                    str(data.media_data_id),
                ),
            )
            await db.commit()
