import asyncio
import psycopg
from pymilvus import connections, utility

from src import config


async def check_psql_connection():
    """Checks the connection to the PostgreSQL database asynchronously."""
    print("Checking PostgreSQL connection...")
    try:
        # Use async connection
        conn = await psycopg.AsyncConnection.connect(
            dbname=config.DB_NAME,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            host=config.DB_HOST,
            port=config.DB_PORT,
            connect_timeout=5,
        )
        await conn.close()
        print("PostgreSQL connection successful.")
    except psycopg.OperationalError as e:
        print(f"PostgreSQL connection failed: {e}")
        raise

def _check_milvus_sync():
    """Synchronous part of milvus check"""
    connections.connect(
        alias="health_check",
        host=config.MILVUS_HOST,
        port=config.MILVUS_PORT,
        timeout=5,
    )
    utility.get_server_version(using="health_check")
    connections.disconnect("health_check")


async def check_milvus_connection():
    """Checks the connection to the Milvus database asynchronously."""
    print("Checking Milvus connection...")
    try:
        # Run synchronous pymilvus code in a separate thread
        await asyncio.to_thread(_check_milvus_sync)
        print("Milvus connection successful.")
    except Exception as e:
        print(f"Milvus connection failed: {e}")
        raise
