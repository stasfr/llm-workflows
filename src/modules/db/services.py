from src.modules.db.common import DB_EXCEPRIONS_LIST
from src.modules.db.repository import DatabasesRepository


async def get_database_list() -> list[str]:
    databases = await DatabasesRepository.get_all()

    filtered_databases = []

    for database in databases:
        if database not in DB_EXCEPRIONS_LIST:
            filtered_databases.append(database)

    return filtered_databases

async def create_new_database_by_name(dbname: str) -> None:
    if not dbname:
        raise ValueError("Database name is required")

    if dbname in DB_EXCEPRIONS_LIST:
        raise ValueError("Database name is not allowed")

    await DatabasesRepository.add_one(dbname)

async def delete_data_base_by_name(dbname: str) -> None:
    if not dbname:
        raise ValueError("Database name is required")

    if dbname in DB_EXCEPRIONS_LIST:
        raise ValueError("Database name is not allowed")

    await DatabasesRepository.delete(dbname)

async def recreate_public_schema(dbname: str) -> None:
    await DatabasesRepository.recreate_public_schema(dbname)

async def create_tables(dbname: str) -> None:
    await DatabasesRepository.create_tables(dbname)
