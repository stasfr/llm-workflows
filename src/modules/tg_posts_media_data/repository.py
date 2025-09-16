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

from src.modules.tg_posts_media_data.schemas import TgPostsMediaDataModel
from src.modules.tg_posts_media_data.dto import AddTgPostsMediaData, UpdateTgPostsMediaData


class TgPostsMediaDataRepository:
    @classmethod
    async def get_all(cls) -> list[TgPostsMediaDataModel]:
        async with await psycopg.AsyncConnection.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
        ) as aconn:
            async with aconn.cursor(row_factory=class_row(TgPostsMediaDataModel)) as acur:
                await acur.execute(sql.SQL("SELECT * FROM media_datas"))
                tg_post_media_data_items = await acur.fetchall()
                return tg_post_media_data_items

    @classmethod
    async def add_one(cls, payload: AddTgPostsMediaData) -> Optional[TgPostsMediaDataModel]:
        description_usage_json = json.dumps(payload.description_usage) if payload.description_usage is not None else None
        tag_usage_json = json.dumps(payload.tag_usage) if payload.tag_usage is not None else None
        structured_description_usage_json = json.dumps(payload.structured_description_usage) if payload.structured_description_usage is not None else None

        async with await psycopg.AsyncConnection.connect(
              user=DB_USER,
              password=DB_PASSWORD,
              host=DB_HOST,
              port=DB_PORT,
              dbname=DB_NAME,
          ) as aconn:
              async with aconn.cursor(row_factory=class_row(TgPostsMediaDataModel)) as acur:
                  await acur.execute(sql.SQL("""
                      INSERT INTO media_datas (media_id, description, tag, structured_description, description_usage, tag_usage, structured_description_usage, description_time, tag_time, structured_description_time)
                      VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                      RETURNING *
                      """), (
                          payload.media_id,
                          payload.description,
                          payload.tag,
                          payload.structured_description,
                          description_usage_json,
                          tag_usage_json,
                          structured_description_usage_json,
                          payload.description_time,
                          payload.tag_time,
                          payload.structured_description_time
                      ))
                  new_tg_post_media_data = await acur.fetchone()
                  return new_tg_post_media_data

    @classmethod
    async def delete(cls, media_data_id: UUID) -> None:
        async with await psycopg.AsyncConnection.connect(
              user=DB_USER,
              password=DB_PASSWORD,
              host=DB_HOST,
              port=DB_PORT,
              dbname=DB_NAME,
          ) as aconn:
              async with aconn.cursor() as acur:
                  await acur.execute(sql.SQL("DELETE FROM media_datas WHERE id = %s"), (media_data_id,))

    @classmethod
    async def update(cls, media_data_id: UUID, payload: UpdateTgPostsMediaData) -> Optional[TgPostsMediaDataModel]:
        description_usage_json = json.dumps(payload.description_usage) if payload.description_usage is not None else None
        tag_usage_json = json.dumps(payload.tag_usage) if payload.tag_usage is not None else None
        structured_description_usage_json = json.dumps(payload.structured_description_usage) if payload.structured_description_usage is not None else None

        async with await psycopg.AsyncConnection.connect(
              user=DB_USER,
              password=DB_PASSWORD,
              host=DB_HOST,
              port=DB_PORT,
              dbname=DB_NAME,
          ) as aconn:
              async with aconn.cursor(row_factory=class_row(TgPostsMediaDataModel)) as acur:
                  await acur.execute(sql.SQL("""
                      UPDATE media_datas
                      SET media_id = %s, description = %s, tag = %s, structured_description = %s, description_usage = %s, tag_usage = %s, structured_description_usage = %s, description_time = %s, tag_time = %s, structured_description_time = %s
                      WHERE id = %s
                      RETURNING *
                      """), (
                          payload.media_id,
                          payload.description,
                          payload.tag,
                          payload.structured_description,
                          description_usage_json,
                          tag_usage_json,
                          structured_description_usage_json,
                          payload.description_time,
                          payload.tag_time,
                          payload.structured_description_time,
                          media_data_id
                      ))
                  updated_tg_post_media_data = await acur.fetchone()
                  return updated_tg_post_media_data

    @classmethod
    async def get_one_by_id(cls, media_data_id: UUID) -> Optional[TgPostsMediaDataModel]:
        async with await psycopg.AsyncConnection.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
        ) as aconn:
            async with aconn.cursor(row_factory=class_row(TgPostsMediaDataModel)) as acur:
                await acur.execute(sql.SQL("SELECT * FROM media_datas WHERE id = %s"), (media_data_id,))
                tg_post_media_data_item = await acur.fetchone()
                return tg_post_media_data_item
