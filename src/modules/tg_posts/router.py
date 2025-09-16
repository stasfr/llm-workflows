from uuid import UUID
from typing import List, Annotated

from fastapi import APIRouter, Body, Path

from src.modules.tg_posts.services import get_all_telegram_posts, add_telegram_post, update_telegram_post, delete_telegram_post, get_telegram_post
from src.modules.tg_posts.schemas import TgPostModel
from src.modules.tg_posts.dto import AddTgPost, UpdateTgPost
from src.schemas import PlainDataResponse, ApiResponse


router = APIRouter(
    prefix="/tg_posts",
    tags=["Telegram Posts"],
)


@router.get("/", description="Get all Telegram posts.")
async def get_all_telegram_posts_handler() -> ApiResponse[List[TgPostModel] | PlainDataResponse]:
    try:
        all_tg_posts = await get_all_telegram_posts()
        return ApiResponse(data=all_tg_posts)
    except Exception as e:
        return ApiResponse(data=PlainDataResponse(error=str(e)))


@router.post("/", description="Add a new Telegram post.")
async def add_telegram_post_handler(
    payload: Annotated[AddTgPost, Body(description="Telegram post creation payload")]
) -> ApiResponse[TgPostModel] | ApiResponse[PlainDataResponse]:
    try:
        new_tg_post = await add_telegram_post(payload)
        return ApiResponse(data=new_tg_post)
    except Exception as e:
        return ApiResponse(data=PlainDataResponse(error=str(e)))


@router.delete("/{post_id}", description="Delete a Telegram post.")
async def delete_telegram_post_handler(
    post_id: Annotated[UUID, Path(
        title="Id of Telegram post (UUID v4)",
        description="Id of the Telegram post to be deleted",
        examples=["3fa85f64-5717-4562-b3fc-2c963f66afa6"]
    )]
) -> ApiResponse[PlainDataResponse]:
    try:
        await delete_telegram_post(post_id)
        return ApiResponse(data=PlainDataResponse(message="Done!"))
    except Exception as e:
        return ApiResponse(data=PlainDataResponse(error=str(e)))


@router.put("/{post_id}", description="Update a Telegram post.")
async def update_telegram_post_handler(
    post_id: Annotated[UUID, Path(
        title="Id of Telegram post (UUID v4)",
        description="Id of the Telegram post to be updated",
        examples=["3fa85f64-5717-4562-b3fc-2c963f66afa6"]
    )],
    payload: Annotated[UpdateTgPost, Body(description="Telegram post update payload")]
) -> ApiResponse[TgPostModel] | ApiResponse[PlainDataResponse]:
    try:
        updated_tg_post = await update_telegram_post(post_id, payload)
        return ApiResponse(data=updated_tg_post)
    except Exception as e:
        return ApiResponse(data=PlainDataResponse(error=str(e)))


@router.get("/{post_id}", description="Get a Telegram post by ID.")
async def get_telegram_post_handler(
    post_id: Annotated[UUID, Path(
        title="Id of Telegram post (UUID v4)",
        description="Id of the Telegram post to be retrieved",
        examples=["3fa85f64-5717-4562-b3fc-2c963f66afa6"]
    )]
) -> ApiResponse[TgPostModel | PlainDataResponse]:
    try:
        tg_post_item = await get_telegram_post(post_id)
        return ApiResponse(data=tg_post_item)
    except Exception as e:
        return ApiResponse(data=PlainDataResponse(error=str(e)))
