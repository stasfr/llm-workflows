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
