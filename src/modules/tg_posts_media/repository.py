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

from src.modules.tg_posts_media.schemas import TgPostMediaModel
from src.modules.tg_posts_media.dto import AddTgPostMedia, UpdateTgPostMedia


class TgPostsMediaRepository:
    @classmethod
    async def get_all(cls) -> list[TgPostMediaModel]:
        async with await psycopg.AsyncConnection.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
        ) as aconn:
            async with aconn.cursor(row_factory=class_row(TgPostMediaModel)) as acur:
                await acur.execute(sql.SQL("SELECT * FROM medias"))
                tg_post_media_items = await acur.fetchall()
                return tg_post_media_items

    @classmethod
    async def add_one(cls, payload: AddTgPostMedia) -> Optional[TgPostMediaModel]:
        async with await psycopg.AsyncConnection.connect(
              user=DB_USER,
              password=DB_PASSWORD,
              host=DB_HOST,
              port=DB_PORT,
              dbname=DB_NAME,
          ) as aconn:
              async with aconn.cursor(row_factory=class_row(TgPostMediaModel)) as acur:
                  await acur.execute(sql.SQL("""
                      INSERT INTO medias (name, post_id, mime_type)
                      VALUES (%s, %s, %s)
                      RETURNING *
                      """), (
                          payload.name,
                          payload.post_id,
                          payload.mime_type,
                      ))
                  new_tg_post_media = await acur.fetchone()
                  return new_tg_post_media

    @classmethod
    async def delete(cls, media_id: UUID) -> None:
        async with await psycopg.AsyncConnection.connect(
              user=DB_USER,
              password=DB_PASSWORD,
              host=DB_HOST,
              port=DB_PORT,
              dbname=DB_NAME,
          ) as aconn:
              async with aconn.cursor() as acur:
                  await acur.execute(sql.SQL("DELETE FROM medias WHERE id = %s"), (media_id,))

    @classmethod
    async def update(cls, media_id: UUID, payload: UpdateTgPostMedia) -> Optional[TgPostMediaModel]:
        async with await psycopg.AsyncConnection.connect(
              user=DB_USER,
              password=DB_PASSWORD,
              host=DB_HOST,
              port=DB_PORT,
              dbname=DB_NAME,
          ) as aconn:
              async with aconn.cursor(row_factory=class_row(TgPostMediaModel)) as acur:
                  await acur.execute(sql.SQL("""
                      UPDATE medias
                      SET name = %s, post_id = %s, mime_type = %s
                      WHERE id = %s
                      RETURNING *
                      """), (
                          payload.name,
                          payload.post_id,
                          payload.mime_type,
                          media_id
                      ))
                  updated_tg_post_media = await acur.fetchone()
                  return updated_tg_post_media

    @classmethod
    async def get_one_by_id(cls, media_id: UUID) -> Optional[TgPostMediaModel]:
        async with await psycopg.AsyncConnection.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
        ) as aconn:
            async with aconn.cursor(row_factory=class_row(TgPostMediaModel)) as acur:
                await acur.execute(sql.SQL("SELECT * FROM medias WHERE id = %s"), (media_id,))
                tg_post_media_item = await acur.fetchone()
                return tg_post_media_item

    @classmethod
    async def get_all_by_post_id(cls, post_id: UUID) -> list[TgPostMediaModel]:
        async with await psycopg.AsyncConnection.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
        ) as aconn:
            async with aconn.cursor(row_factory=class_row(TgPostMediaModel)) as acur:
                await acur.execute(sql.SQL("SELECT * FROM medias WHERE post_id = %s"), (post_id,))
                tg_post_media_items = await acur.fetchall()
                return tg_post_media_items
