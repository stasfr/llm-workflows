from typing import List
from uuid import UUID

from src.modules.tg_posts_media.repository import TgPostsMediaRepository
from src.modules.tg_posts_media.schemas import TgPostMediaModel
from src.modules.tg_posts_media.dto import AddTgPostMedia, UpdateTgPostMedia


async def get_all_telegram_posts_media() -> List[TgPostMediaModel]:
    all_tg_posts_media = await TgPostsMediaRepository.get_all()
    return all_tg_posts_media

async def add_telegram_post_media(payload: AddTgPostMedia) -> TgPostMediaModel:
    new_tg_post_media = await TgPostsMediaRepository.add_one(payload)

    if not new_tg_post_media:
        raise ValueError("Failed to create Telegram post media")

    return new_tg_post_media

async def delete_telegram_post_media(media_id: UUID) -> None:
    await TgPostsMediaRepository.delete(media_id)

async def update_telegram_post_media(media_id: UUID, payload: UpdateTgPostMedia) -> TgPostMediaModel:
    updated_tg_post_media = await TgPostsMediaRepository.update(media_id, payload)

    if not updated_tg_post_media:
        raise ValueError("Failed to update Telegram post media")

    return updated_tg_post_media

async def get_telegram_post_media(media_id: UUID) -> TgPostMediaModel:
    tg_post_media_item = await TgPostsMediaRepository.get_one_by_id(media_id)

    if not tg_post_media_item:
        raise ValueError("Telegram post media not found")

    return tg_post_media_item
