from typing import List
from uuid import UUID
from src.config import DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME
import psycopg
from psycopg import sql
from psycopg.rows import dict_row

from src.modules.embeddings.schemas import PostForEmbedding, PostMediaForEmbedding


class PostEmbeddingsRepository:
    @classmethod
    async def get_posts_for_embedding_by_export_id(cls, export_id: UUID, limit: int, offset: int) -> List[PostForEmbedding]:
        async with await psycopg.AsyncConnection.connect(
            user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT, dbname=DB_NAME
        ) as aconn:
            async with aconn.cursor(row_factory=dict_row) as acur:
                await acur.execute(sql.SQL("""
                    SELECT p.id as post_id, p.post_text, te.photos_path
                    FROM posts p
                    JOIN tg_exports te ON p.from_id = te.id
                    WHERE te.id = %s
                    ORDER BY p.id
                    LIMIT %s OFFSET %s
                """), (export_id, limit, offset))
                result = await acur.fetchall()
                return [PostForEmbedding(**row) for row in result]

    @classmethod
    async def get_media_for_post(cls, post_id: UUID) -> List[PostMediaForEmbedding]:
        async with await psycopg.AsyncConnection.connect(
            user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT, dbname=DB_NAME
        ) as aconn:
            async with aconn.cursor(row_factory=dict_row) as acur:
                await acur.execute(sql.SQL("""
                    SELECT m.id as media_id, m.name as media_name, md.description
                    FROM medias m
                    LEFT JOIN media_datas md ON m.id = md.media_id
                    WHERE m.post_id = %s AND m.mime_type LIKE 'image/%%'
                """), (post_id,))
                result = await acur.fetchall()
                return [PostMediaForEmbedding(**row) for row in result]
