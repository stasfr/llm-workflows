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

from src.modules.jobs.schemas import JobModel
from src.modules.jobs.schemas import AddJob, UpdateJobStatus


class JobsRepository:
    @classmethod
    async def get_all(cls) -> list[JobModel]:
        async with await psycopg.AsyncConnection.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
        ) as aconn:
            async with aconn.cursor(row_factory=class_row(JobModel)) as acur:
                await acur.execute(sql.SQL("""
                    SELECT * FROM jobs
                    ORDER BY created_at DESC
                """))
                job_items = await acur.fetchall()
                return job_items

    @classmethod
    async def add_one(cls, payload: AddJob) -> Optional[JobModel]:
        async with await psycopg.AsyncConnection.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
        ) as aconn:
            async with aconn.cursor(row_factory=class_row(JobModel)) as acur:
                await acur.execute(sql.SQL("""
                      INSERT INTO jobs (status, metadata)
                      VALUES (%s, %s)
                      RETURNING *
                      """), (
                    payload.status,
                    payload.metadata
                ))
                new_job = await acur.fetchone()
                return new_job

    @classmethod
    async def delete(cls, job_id: UUID) -> None:
        async with await psycopg.AsyncConnection.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
        ) as aconn:
            async with aconn.cursor() as acur:
                await acur.execute(sql.SQL("DELETE FROM jobs WHERE id = %s"), (job_id,))

    @classmethod
    async def update_status(cls, job_id: UUID, payload: UpdateJobStatus) -> Optional[JobModel]:
        async with await psycopg.AsyncConnection.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
        ) as aconn:
            async with aconn.cursor(row_factory=class_row(JobModel)) as acur:
                await acur.execute(sql.SQL("""
                      UPDATE jobs
                      SET status = %s, updated_at = NOW() AT TIME ZONE 'UTC'
                      WHERE id = %s
                      RETURNING *
                      """), (
                    payload.status,
                    job_id
                ))
                updated_job = await acur.fetchone()
                return updated_job

    @classmethod
    async def get_one_by_id(cls, job_id: UUID) -> Optional[JobModel]:
        async with await psycopg.AsyncConnection.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
        ) as aconn:
            async with aconn.cursor(row_factory=class_row(JobModel)) as acur:
                await acur.execute(sql.SQL("SELECT * FROM jobs WHERE id = %s"), (job_id,))
                job_item = await acur.fetchone()
                return job_item
