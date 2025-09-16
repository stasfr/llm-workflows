from typing import List
from uuid import UUID

from src.modules.tg_posts.repository import TgPostsRepository
from src.modules.tg_posts.schemas import TgPostModel
from src.modules.tg_posts.dto import AddTgPost, UpdateTgPost


async def get_all_telegram_posts() -> List[TgPostModel]:
    all_tg_posts = await TgPostsRepository.get_all()
    return all_tg_posts

async def add_telegram_post(payload: AddTgPost) -> TgPostModel:
    new_tg_post = await TgPostsRepository.add_one(payload)

    if not new_tg_post:
        raise ValueError("Failed to create Telegram post")

    return new_tg_post

async def delete_telegram_post(post_id: UUID) -> None:
    await TgPostsRepository.delete(post_id)

async def update_telegram_post(post_id: UUID, payload: UpdateTgPost) -> TgPostModel:
    updated_tg_post = await TgPostsRepository.update(post_id, payload)

    if not updated_tg_post:
        raise ValueError("Failed to update Telegram post")

    return updated_tg_post

async def get_telegram_post(post_id: UUID) -> TgPostModel:
    tg_post_item = await TgPostsRepository.get_one_by_id(post_id)

    if not tg_post_item:
        raise ValueError("Telegram post not found")

    return tg_post_item
