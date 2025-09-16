from uuid import UUID
from typing import List, Annotated

from fastapi import APIRouter, Body, Path

from src.modules.tg_posts_media.services import get_all_telegram_posts_media, add_telegram_post_media, update_telegram_post_media, delete_telegram_post_media, get_telegram_post_media, get_telegram_posts_media_by_post_id
from src.modules.tg_posts_media.schemas import TgPostMediaModel
from src.modules.tg_posts_media.dto import AddTgPostMedia, UpdateTgPostMedia
from src.schemas import PlainDataResponse, ApiResponse


router = APIRouter(
    prefix="/tg_posts_media",
    tags=["Telegram Posts Media"],
)


@router.get("/", description="Get all Telegram posts media.")
async def get_all_telegram_posts_media_handler() -> ApiResponse[List[TgPostMediaModel] | PlainDataResponse]:
    try:
        all_tg_posts_media = await get_all_telegram_posts_media()
        return ApiResponse(data=all_tg_posts_media)
    except Exception as e:
        return ApiResponse(data=PlainDataResponse(error=str(e)))


@router.post("/", description="Add a new Telegram post media.")
async def add_telegram_post_media_handler(
    payload: Annotated[AddTgPostMedia, Body(description="Telegram post media creation payload")]
) -> ApiResponse[TgPostMediaModel] | ApiResponse[PlainDataResponse]:
    try:
        new_tg_post_media = await add_telegram_post_media(payload)
        return ApiResponse(data=new_tg_post_media)
    except Exception as e:
        return ApiResponse(data=PlainDataResponse(error=str(e)))


@router.delete("/{media_id}", description="Delete a Telegram post media.")
async def delete_telegram_post_media_handler(
    media_id: Annotated[UUID, Path(
        title="Id of Telegram post media (UUID v4)",
        description="Id of the Telegram post media to be deleted",
        examples=["3fa85f64-5717-4562-b3fc-2c963f66afa6"]
    )]
) -> ApiResponse[PlainDataResponse]:
    try:
        await delete_telegram_post_media(media_id)
        return ApiResponse(data=PlainDataResponse(message="Done!"))
    except Exception as e:
        return ApiResponse(data=PlainDataResponse(error=str(e)))


@router.put("/{media_id}", description="Update a Telegram post media.")
async def update_telegram_post_media_handler(
    media_id: Annotated[UUID, Path(
        title="Id of Telegram post media (UUID v4)",
        description="Id of the Telegram post media to be updated",
        examples=["3fa85f64-5717-4562-b3fc-2c963f66afa6"]
    )],
    payload: Annotated[UpdateTgPostMedia, Body(description="Telegram post media update payload")]
) -> ApiResponse[TgPostMediaModel] | ApiResponse[PlainDataResponse]:
    try:
        updated_tg_post_media = await update_telegram_post_media(media_id, payload)
        return ApiResponse(data=updated_tg_post_media)
    except Exception as e:
        return ApiResponse(data=PlainDataResponse(error=str(e)))


@router.get("/{media_id}", description="Get a Telegram post media by ID.")
async def get_telegram_post_media_handler(
    media_id: Annotated[UUID, Path(
        title="Id of Telegram post media (UUID v4)",
        description="Id of the Telegram post media to be retrieved",
        examples=["3fa85f64-5717-4562-b3fc-2c963f66afa6"]
    )]
) -> ApiResponse[TgPostMediaModel | PlainDataResponse]:
    try:
        tg_post_media_item = await get_telegram_post_media(media_id)
        return ApiResponse(data=tg_post_media_item)
    except Exception as e:
        return ApiResponse(data=PlainDataResponse(error=str(e)))


@router.get("/by_post/{post_id}", description="Get all Telegram posts media by post ID.")
async def get_telegram_posts_media_by_post_id_handler(
    post_id: Annotated[UUID, Path(
        title="Id of Telegram post (UUID v4)",
        description="Id of the Telegram post to be retrieved",
        examples=["3fa85f64-5717-4562-b3fc-2c963f66afa6"]
    )]
) -> ApiResponse[List[TgPostMediaModel] | PlainDataResponse]:
    try:
        tg_post_media_items = await get_telegram_posts_media_by_post_id(post_id)
        return ApiResponse(data=tg_post_media_items)
    except Exception as e:
        return ApiResponse(data=PlainDataResponse(error=str(e)))
