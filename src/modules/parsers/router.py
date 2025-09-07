from fastapi import APIRouter

from src.schemas import ApiResponse, PlainDataResponse

from src.modules.db.schemas import SProject
from src.parsers.parse_raw_telegram_data import parse_raw_telegram_data


router = APIRouter(
    prefix="/parser",
    tags=["Parsers"],
)


@router.post("/parse_telegram_data", response_model=ApiResponse[PlainDataResponse], description="Parses raw data from Telegram for a project.")
def parse_telegram_data_handler(
    project: SProject,
) -> ApiResponse[PlainDataResponse]:
    try:
        parse_raw_telegram_data(project_name=project.name, project_snapshot=project.snapshot)
        return ApiResponse(data=PlainDataResponse(message=f"Data for project {project.name}_{project.snapshot} parsed successfully"))
    except Exception as e:
        return ApiResponse(data=PlainDataResponse(error=str(e)))
