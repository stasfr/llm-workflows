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

from src.modules.tg_posts.schemas import TgPostModel
from src.modules.tg_posts.dto import AddTgPost, UpdateTgPost


class TgPostsRepository:
    @classmethod
    async def get_all(cls) -> list[TgPostModel]:
        async with await psycopg.AsyncConnection.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
        ) as aconn:
            async with aconn.cursor(row_factory=class_row(TgPostModel)) as acur:
                await acur.execute(sql.SQL("SELECT * FROM posts"))
                tg_post_items = await acur.fetchall()
                return tg_post_items

    @classmethod
    async def add_one(cls, payload: AddTgPost) -> Optional[TgPostModel]:
        reactions_json = (
            json.dumps([r.model_dump() for r in payload.reactions])
            if payload.reactions is not None
            else None
        )
        async with await psycopg.AsyncConnection.connect(
              user=DB_USER,
              password=DB_PASSWORD,
              host=DB_HOST,
              port=DB_PORT,
              dbname=DB_NAME,
          ) as aconn:
              async with aconn.cursor(row_factory=class_row(TgPostModel)) as acur:
                  await acur.execute(sql.SQL("""
                      INSERT INTO posts (post_id, from_id, date, edited, post_text, reactions)
                      VALUES (%s, %s, %s, %s, %s, %s)
                      RETURNING *
                      """), (
                          payload.post_id,
                          payload.from_id,
                          payload.date,
                          payload.edited,
                          payload.post_text,
                          reactions_json
                      ))
                  new_tg_post = await acur.fetchone()
                  return new_tg_post

    @classmethod
    async def delete(cls, post_id: UUID) -> None:
        async with await psycopg.AsyncConnection.connect(
              user=DB_USER,
              password=DB_PASSWORD,
              host=DB_HOST,
              port=DB_PORT,
              dbname=DB_NAME,
          ) as aconn:
              async with aconn.cursor() as acur:
                  await acur.execute(sql.SQL("DELETE FROM posts WHERE id = %s"), (post_id,))

    @classmethod
    async def update(cls, post_id: UUID, payload: UpdateTgPost) -> Optional[TgPostModel]:
        reactions_json = (
            json.dumps([r.model_dump() for r in payload.reactions])
            if payload.reactions is not None
            else None
        )
        async with await psycopg.AsyncConnection.connect(
              user=DB_USER,
              password=DB_PASSWORD,
              host=DB_HOST,
              port=DB_PORT,
              dbname=DB_NAME,
          ) as aconn:
              async with aconn.cursor(row_factory=class_row(TgPostModel)) as acur:
                  await acur.execute(sql.SQL("""
                      UPDATE posts
                      SET post_id = %s, from_id = %s, date = %s, edited = %s, post_text = %s, reactions = %s
                      WHERE id = %s
                      RETURNING *
                      """), (
                          payload.post_id,
                          payload.from_id,
                          payload.date,
                          payload.edited,
                          payload.post_text,
                          reactions_json,
                          post_id
                      ))
                  updated_tg_post = await acur.fetchone()
                  return updated_tg_post

    @classmethod
    async def get_one_by_id(cls, post_id: UUID) -> Optional[TgPostModel]:
        async with await psycopg.AsyncConnection.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
        ) as aconn:
            async with aconn.cursor(row_factory=class_row(TgPostModel)) as acur:
                await acur.execute(sql.SQL("SELECT * FROM posts WHERE id = %s"), (post_id,))
                tg_post_item = await acur.fetchone()
                return tg_post_item
