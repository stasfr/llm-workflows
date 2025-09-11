import json
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

from src.modules.parsers.schemas import PostModel
from src.modules.parsers.dto import CreatePost


class ParsersRepository:
    @classmethod
    async def add_one_post_with_media(cls, tg_export_id: UUID, payload: CreatePost) -> Optional[PostModel]:
        reactions_json = json.dumps(payload.reactions) if payload.reactions is not None else None

        async with await psycopg.AsyncConnection.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
        ) as aconn:
            async with aconn.cursor(row_factory=class_row(PostModel)) as acur:
                await acur.execute(sql.SQL("""
                    INSERT INTO posts (post_id, date, edited, post_text, reactions, from_id)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING *
                    """), (payload.post_id, payload.date, payload.edited, payload.post_text, reactions_json, tg_export_id))
                new_post = await acur.fetchone()

                return new_post
