from typing import Annotated

from fastapi import APIRouter, Path

from src.schemas import ApiResponse, PlainDataResponse

from src.modules.db_psql.services import (
    create_new_database_by_name,
    delete_data_base_by_name,
    get_database_list,
    create_tables,
    recreate_public_schema,
    setup_database
)


router = APIRouter(
    prefix="/db",
    tags=["Postgres DB Operations"],
)


@router.get("/databases", description="Get all databases names in psql container")
async def get_database_list_handler() -> ApiResponse[list[str] | PlainDataResponse]:
    try:
        databases = await get_database_list()
        return ApiResponse(data=databases)
    except Exception as e:
        return ApiResponse(data=PlainDataResponse(error=str(e)))

@router.post("/create_new_database/{dbname}", description="Initialize new database inside psql container with given name")
async def create_new_database_handler(
    dbname: Annotated[str, Path(
        title="Database Name",
        description="Name of the database to be created",
        examples=["mydb"],
    )]
) -> ApiResponse[PlainDataResponse]:
    try:
        await create_new_database_by_name(dbname)
        return ApiResponse(data=PlainDataResponse(message=f"Done!"))
    except Exception as e:
        return ApiResponse(data=PlainDataResponse(error=str(e)))

@router.delete("/delete_database/{dbname}", description="Delete database inside psql container with given name")
async def delete_database_handler(
    dbname: Annotated[str, Path(
        title="Database Name",
        description="Name of the database to be deleted",
        examples=["mydb"],
    )]
) -> ApiResponse[PlainDataResponse]:
    try:
        await delete_data_base_by_name(dbname)
        return ApiResponse(data=PlainDataResponse(message=f"Done!"))
    except Exception as e:
        return ApiResponse(data=PlainDataResponse(error=str(e)))

@router.post("/recreate_public_schema/{dbname}", description="Recreate public schema in given database")
async def recreate_public_schema_handler(
    dbname: Annotated[str, Path(
        title="Database Name",
        description="Name of the database to recreate public schema in",
        examples=["mydb"],
    )]
) -> ApiResponse[PlainDataResponse]:
    try:
        await recreate_public_schema(dbname)
        return ApiResponse(data=PlainDataResponse(message=f"Done!"))
    except Exception as e:
        return ApiResponse(data=PlainDataResponse(error=str(e)))

@router.post("/create_tables/{dbname}", description="Initialize all tables in given database")
async def create_tables_handler(
    dbname: Annotated[str, Path(
        title="Database Name",
        description="Name of the database to initialize tables in",
        examples=["mydb"],
    )]
) -> ApiResponse[PlainDataResponse]:
    try:
        await create_tables(dbname)
        return ApiResponse(data=PlainDataResponse(message=f"Done!"))
    except Exception as e:
        return ApiResponse(data=PlainDataResponse(error=str(e)))

@router.post("/setup_db/{dbname}", description="Setup database with full cycle: create/recreate and initialize tables")
async def setup_database_handler(
    dbname: Annotated[str, Path(
        title="Database Name",
        description="Name of the database to setup",
        examples=["mydb"],
    )]
) -> ApiResponse[PlainDataResponse]:
    try:
        await setup_database(dbname)
        return ApiResponse(data=PlainDataResponse(message=f"Database {dbname} setup completed successfully!"))
    except Exception as e:
        return ApiResponse(data=PlainDataResponse(error=str(e)))
