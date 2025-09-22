from typing import Annotated

from fastapi import APIRouter, Body

from src.modules.parsers.services import parse_raw_telegram_data
from src.modules.parsers.dto import StartParsing

from src.schemas import PlainDataResponse, ApiResponse


router = APIRouter(
    prefix="/parser",
    tags=["Parsers"],
)


@router.post("/tg_data", description="Parses raw data from Telegram for a project and save it to SQLite database for the experiment")
async def parse_telegram_data_handler(payload: Annotated[StartParsing, Body()]) -> ApiResponse[PlainDataResponse]:
    try:
        await parse_raw_telegram_data(payload)
        return ApiResponse(data=PlainDataResponse(message=f"Done"))
    except Exception as e:
        return ApiResponse(data=PlainDataResponse(error=str(e)))
