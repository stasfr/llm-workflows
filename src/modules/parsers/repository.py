import json
from typing import Optional, List
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

from src.modules.parsers.schemas import PostModel
from src.modules.parsers.dto import CreatePost


class ParsersRepository:
    @classmethod
    async def add_one_post_with_media(cls, tg_export_id: UUID, payload: CreatePost) -> Optional[PostModel]:
        reactions_json = (
            json.dumps([r.model_dump() for r in payload.reactions])
            if payload.reactions is not None
            else None
        )
        media_names: List[str] = []
        media_mime_types: List[Optional[str]] = []

        if payload.media:
            media_names = [media.name for media in payload.media]
            media_mime_types = [media.mime_type for media in payload.media]


        async with await psycopg.AsyncConnection.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
        ) as aconn:
            async with aconn.cursor(row_factory=class_row(PostModel)) as acur:
                stmt = sql.SQL("""
                    WITH new_post AS (
                        INSERT INTO posts (post_id, date, edited, post_text, reactions, has_media, from_id)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        RETURNING *
                    ),
                    new_media AS (
                        INSERT INTO medias (name, mime_type, post_id)
                        SELECT
                            t.media_name,
                            t.media_mime_type,
                            new_post.id
                        FROM
                            new_post,
                            unnest(%s::text[], %s::text[]) AS t(media_name, media_mime_type)
                        RETURNING id
                    ),
                    new_media_data AS (
                        INSERT INTO media_datas (media_id)
                        SELECT id FROM new_media
                        RETURNING id
                    )

                    SELECT * FROM new_post;
                    """)

                await acur.execute(
                    stmt,
                    (
                        payload.post_id,
                        payload.date,
                        payload.edited,
                        payload.post_text,
                        reactions_json,
                        payload.has_media,
                        tg_export_id,
                        media_names,
                        media_mime_types
                    )
                )

                new_post = await acur.fetchone()
                return new_post
