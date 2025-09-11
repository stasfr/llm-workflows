from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Path, Body

from src.modules.parsers.services import parse_raw_telegram_data
from src.modules.parsers.dto import StartParsing

from src.schemas import PlainDataResponse, ApiResponse


router = APIRouter(
    prefix="/parser",
    tags=["Parsers"],
)


@router.post("/tg_data/{tg_export_id}", description="Parses raw data from Telegram for a project and save it to psql")
async def parse_telegram_data_handler(
    tg_export_id: Annotated[UUID, Path(
        title="Id of Telegram export (UUID v4)",
        description="Id of the Telegram export to be parsed",
        examples=["3fa85f64-5717-4562-b3fc-2c963f66afa6"]
    )],
    payload: Annotated[StartParsing, Body()]
) -> ApiResponse[PlainDataResponse]:
    try:
        await parse_raw_telegram_data(tg_export_id, payload)
        return ApiResponse(data=PlainDataResponse(message=f"Done"))
    except Exception as e:
        return ApiResponse(data=PlainDataResponse(error=str(e)))
