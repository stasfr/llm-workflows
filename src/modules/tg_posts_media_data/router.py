from uuid import UUID
from typing import List, Annotated

from fastapi import APIRouter, Body, Path

from src.modules.tg_posts_media_data.services import get_all_telegram_posts_media_data, add_telegram_post_media_data, update_telegram_post_media_data, delete_telegram_post_media_data, get_telegram_post_media_data
from src.modules.tg_posts_media_data.schemas import TgPostsMediaDataModel
from src.modules.tg_posts_media_data.dto import AddTgPostsMediaData, UpdateTgPostsMediaData
from src.schemas import PlainDataResponse, ApiResponse


router = APIRouter(
    prefix="/tg_posts_media_data",
    tags=["Telegram Posts Media Data"],
)


@router.get("/", description="Get all Telegram posts media data.")
async def get_all_telegram_posts_media_data_handler() -> ApiResponse[List[TgPostsMediaDataModel] | PlainDataResponse]:
    try:
        all_tg_posts_media_data = await get_all_telegram_posts_media_data()
        return ApiResponse(data=all_tg_posts_media_data)
    except Exception as e:
        return ApiResponse(data=PlainDataResponse(error=str(e)))


@router.post("/", description="Add a new Telegram post media data.")
async def add_telegram_post_media_data_handler(
    payload: Annotated[AddTgPostsMediaData, Body(description="Telegram post media data creation payload")]
) -> ApiResponse[TgPostsMediaDataModel] | ApiResponse[PlainDataResponse]:
    try:
        new_tg_post_media_data = await add_telegram_post_media_data(payload)
        return ApiResponse(data=new_tg_post_media_data)
    except Exception as e:
        return ApiResponse(data=PlainDataResponse(error=str(e)))


@router.delete("/{media_data_id}", description="Delete a Telegram post media data.")
async def delete_telegram_post_media_data_handler(
    media_data_id: Annotated[UUID, Path(
        title="Id of Telegram post media data (UUID v4)",
        description="Id of the Telegram post media data to be deleted",
        examples=["3fa85f64-5717-4562-b3fc-2c963f66afa6"]
    )]
) -> ApiResponse[PlainDataResponse]:
    try:
        await delete_telegram_post_media_data(media_data_id)
        return ApiResponse(data=PlainDataResponse(message="Done!"))
    except Exception as e:
        return ApiResponse(data=PlainDataResponse(error=str(e)))


@router.put("/{media_data_id}", description="Update a Telegram post media data.")
async def update_telegram_post_media_data_handler(
    media_data_id: Annotated[UUID, Path(
        title="Id of Telegram post media data (UUID v4)",
        description="Id of the Telegram post media data to be updated",
        examples=["3fa85f64-5717-4562-b3fc-2c963f66afa6"]
    )],
    payload: Annotated[UpdateTgPostsMediaData, Body(description="Telegram post media data update payload")]
) -> ApiResponse[TgPostsMediaDataModel] | ApiResponse[PlainDataResponse]:
    try:
        updated_tg_post_media_data = await update_telegram_post_media_data(media_data_id, payload)
        return ApiResponse(data=updated_tg_post_media_data)
    except Exception as e:
        return ApiResponse(data=PlainDataResponse(error=str(e)))


@router.get("/{media_data_id}", description="Get a Telegram post media data by ID.")
async def get_telegram_post_media_data_handler(
    media_data_id: Annotated[UUID, Path(
        title="Id of Telegram post media data (UUID v4)",
        description="Id of the Telegram post media data to be retrieved",
        examples=["3fa85f64-5717-4562-b3fc-2c963f66afa6"]
    )]
) -> ApiResponse[TgPostsMediaDataModel | PlainDataResponse]:
    try:
        tg_post_media_data_item = await get_telegram_post_media_data(media_data_id)
        return ApiResponse(data=tg_post_media_data_item)
    except Exception as e:
        return ApiResponse(data=PlainDataResponse(error=str(e)))
