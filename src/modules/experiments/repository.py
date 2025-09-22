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

from src.modules.experiments.schemas import ExperimentModel
from src.modules.experiments.dto import AddExperiment, UpdateExperiment


class ExperimentsRepository:
    @classmethod
    async def get_all(cls) -> list[ExperimentModel]:
        async with await psycopg.AsyncConnection.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
        ) as aconn:
            async with aconn.cursor(row_factory=class_row(ExperimentModel)) as acur:
                await acur.execute(sql.SQL("""
                    SELECT * FROM experiments
                    """))
                experiment_items = await acur.fetchall()
                return experiment_items

    @classmethod
    async def add_one(cls, payload: AddExperiment) -> Optional[ExperimentModel]:
        async with await psycopg.AsyncConnection.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
        ) as aconn:
            async with aconn.cursor(row_factory=class_row(ExperimentModel)) as acur:
                await acur.execute(sql.SQL("""
                      INSERT INTO experiments (tg_export_id, sqlite_path, milvus_collection_name, meta_data)
                      VALUES (%s, %s, %s, %s)
                      RETURNING *
                      """), (payload.tg_export_id, payload.sqlite_path, payload.milvus_collection_name, payload.meta_data))
                new_experiment = await acur.fetchone()
                return new_experiment

    @classmethod
    async def delete(cls, experiment_id: UUID) -> None:
        async with await psycopg.AsyncConnection.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
        ) as aconn:
            async with aconn.cursor() as acur:
                await acur.execute(sql.SQL("""
                      DELETE FROM experiments WHERE id = %s
                      """), (experiment_id,))

    @classmethod
    async def update(cls, experiment_id: UUID, payload: UpdateExperiment) -> Optional[ExperimentModel]:
        async with await psycopg.AsyncConnection.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
        ) as aconn:
            async with aconn.cursor(row_factory=class_row(ExperimentModel)) as acur:
                await acur.execute(sql.SQL("""
                      UPDATE experiments
                      SET tg_export_id = %s, sqlite_path = %s, milvus_collection_name = %s,
                          meta_data = %s, updated_at = NOW() AT TIME ZONE 'UTC'
                      WHERE id = %s
                      RETURNING *
                      """), (payload.tg_export_id, payload.sqlite_path, payload.milvus_collection_name,
                             payload.meta_data, experiment_id))
                updated_experiment = await acur.fetchone()
                return updated_experiment

    @classmethod
    async def get_one_by_id(cls, experiment_id: UUID) -> Optional[ExperimentModel]:
        async with await psycopg.AsyncConnection.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
        ) as aconn:
            async with aconn.cursor(row_factory=class_row(ExperimentModel)) as acur:
                await acur.execute(sql.SQL("""
                    SELECT * FROM experiments
                    WHERE id = %s
                    """), (experiment_id,))
                experiment_item = await acur.fetchone()
                return experiment_item

    @classmethod
    async def get_by_tg_export_id(cls, tg_export_id: UUID) -> List[ExperimentModel]:
        async with await psycopg.AsyncConnection.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
        ) as aconn:
            async with aconn.cursor(row_factory=class_row(ExperimentModel)) as acur:
                await acur.execute(sql.SQL("""
                    SELECT * FROM experiments
                    WHERE tg_export_id = %s
                    ORDER BY created_at DESC
                    """), (tg_export_id,))
                experiment_items = await acur.fetchall()
                return experiment_items
