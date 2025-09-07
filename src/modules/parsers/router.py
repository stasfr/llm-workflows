from typing import Annotated

from fastapi import APIRouter, Depends

from src.schemas import ApiResponse, PlainDataResponse

from src.modules.db.schemas import SProject
from src.modules.parsers.services import parse_raw_telegram_data


router = APIRouter(
    prefix="/parser",
    tags=["Parsers"],
)


@router.post("/parse_telegram_data", response_model=ApiResponse[PlainDataResponse], description="Parses raw data from Telegram for a project.")
def parse_telegram_data_handler(
    project: Annotated[SProject, Depends()],
) -> ApiResponse[PlainDataResponse]:
    try:
        parse_raw_telegram_data(project_name=project.project_name, project_snapshot=project.project_snapshot)
        return ApiResponse(data=PlainDataResponse(message=f"Data for project {project.project_name}_{project.project_snapshot} parsed successfully"))
    except Exception as e:
        return ApiResponse(data=PlainDataResponse(error=str(e)))
