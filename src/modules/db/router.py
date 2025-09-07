from fastapi import APIRouter

from src.schemas import ApiResponse, PlainDataResponse

from src.modules.db.schemas import SProject
from src.db.db import init_db, init_experiments_db


router = APIRouter(
    prefix="/db",
    tags=["Databases"],
)


@router.post("/init", response_model=ApiResponse[PlainDataResponse], description="Initialize a database")
def init_db_handler(
    project: SProject,
) -> ApiResponse[PlainDataResponse]:
    db_name = f"{project.name}_{project.snapshot}"
    try:
        init_db(db_name)
        return ApiResponse(data=PlainDataResponse(message=f"Database for project {project.name}_{project.snapshot} initialized successfully"))
    except Exception as e:
        return ApiResponse(data=PlainDataResponse(error=str(e)))

@router.post("/expirements/init", response_model=ApiResponse[PlainDataResponse], description="Initialize experiment database")
def init_experiments_db_handler() -> ApiResponse[PlainDataResponse]:
    try:
        init_experiments_db()
        return ApiResponse(data=PlainDataResponse(message="Experiment Database initialized successfully"))
    except Exception as e:
        return ApiResponse(data=PlainDataResponse(error=str(e)))
