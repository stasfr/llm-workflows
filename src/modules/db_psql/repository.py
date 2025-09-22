from src.config import (
    DB_USER,
    DB_PASSWORD,
    DB_HOST,
    DB_PORT,
)

import psycopg
from psycopg import sql


class DatabasesRepository:
    @classmethod
    async def get_all(cls) -> list[str]:
        aconn = await psycopg.AsyncConnection.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            dbname="postgres",
            autocommit=True
        )
        acur = aconn.cursor()

        await acur.execute(sql.SQL("""
            SELECT datname FROM pg_database
            """))
        result = await acur.fetchall()

        await acur.close()
        await aconn.close()

        return [row[0] for row in result]

    @classmethod
    async def add_one(cls, dbname: str) -> None:
        aconn = await psycopg.AsyncConnection.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            dbname="postgres",
            autocommit=True
        )
        acur = aconn.cursor()

        await acur.execute(sql.SQL("""
            CREATE DATABASE {dbname}
            """).format(
            dbname=sql.Identifier(dbname)
        ))
        await aconn.commit()

        await acur.close()
        await aconn.close()

    @classmethod
    async def delete(cls, dbname: str) -> None:
        aconn = await psycopg.AsyncConnection.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            dbname="postgres",
            autocommit=True
        )
        acur = aconn.cursor()

        await acur.execute(sql.SQL("""
            DROP DATABASE IF EXISTS {dbname}
            """).format(
            dbname=sql.Identifier(dbname)
        ))
        await aconn.commit()

        await acur.close()
        await aconn.close()

    @classmethod
    async def recreate_public_schema(cls, dbname: str) -> None:
        async with await psycopg.AsyncConnection.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            dbname=dbname,
        ) as aconn:
            async with aconn.cursor() as acur:
                await acur.execute(sql.SQL("""
                    DROP SCHEMA public CASCADE;
                    CREATE SCHEMA public;
                    """))

    @classmethod
    async def create_tables(cls, dbname: str) -> None:
        async with await psycopg.AsyncConnection.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            dbname=dbname,
        ) as aconn:
            async with aconn.cursor() as acur:
                await acur.execute(sql.SQL("""
                    CREATE TABLE IF NOT EXISTS tg_exports (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

                        channel_id VARCHAR(255) NOT NULL UNIQUE,
                        data_path VARCHAR(255) NOT NULL,
                        photos_path VARCHAR(255) NOT NULL,

                        created_at TIMESTAMPTZ DEFAULT (NOW() AT TIME ZONE 'UTC')
                    )
                    """))

                await acur.execute(sql.SQL("""
                    CREATE TABLE IF NOT EXISTS posts (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

                        post_id INTEGER NOT NULL,
                        date TIMESTAMPTZ,
                        edited TIMESTAMPTZ,
                        post_text TEXT,
                        reactions JSONB,
                        has_media BOOLEAN DEFAULT FALSE,

                        from_id UUID,
                        FOREIGN KEY (from_id) REFERENCES tg_exports(id) ON DELETE SET NULL,

                        created_at TIMESTAMPTZ DEFAULT (NOW() AT TIME ZONE 'UTC')
                    )
                    """))

                await acur.execute(sql.SQL("""
                    CREATE TABLE IF NOT EXISTS medias (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

                        name TEXT NOT NULL,
                        mime_type TEXT,

                        post_id UUID,
                        FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE SET NULL,

                        created_at TIMESTAMPTZ DEFAULT (NOW() AT TIME ZONE 'UTC')
                    )
                    """))

                await acur.execute(sql.SQL("""
                    CREATE TABLE IF NOT EXISTS media_datas (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

                        description TEXT,
                        tag TEXT,
                        structured_description TEXT,
                        description_usage JSONB,
                        tag_usage JSONB,
                        structured_description_usage JSONB,
                        description_time REAL,
                        tag_time REAL,
                        structured_description_time REAL,

                        media_id UUID,
                        FOREIGN KEY (media_id) REFERENCES medias(id) ON DELETE SET NULL,

                        created_at TIMESTAMPTZ DEFAULT (NOW() AT TIME ZONE 'UTC')
                    )
                    """))

                await acur.execute(sql.SQL("""
                    CREATE TABLE IF NOT EXISTS jobs (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

                        status VARCHAR(50) NOT NULL DEFAULT 'pending',
                        metadata TEXT,

                        created_at TIMESTAMPTZ DEFAULT (NOW() AT TIME ZONE 'UTC'),
                        updated_at TIMESTAMPTZ
                    )
                    """))

                await acur.execute(sql.SQL("""
                    CREATE TABLE IF NOT EXISTS experiments (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

                        tg_export_id UUID,
                        FOREIGN KEY (tg_export_id) REFERENCES tg_exports(id) ON DELETE SET NULL,

                        milvus_collection_name TEXT NOT NULL,
                        meta_data JSONB,

                        created_at TIMESTAMPTZ DEFAULT (NOW() AT TIME ZONE 'UTC'),
                        updated_at TIMESTAMPTZ
                    )
                    """))
