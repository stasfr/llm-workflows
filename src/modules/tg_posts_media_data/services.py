from typing import List
from uuid import UUID

from src.modules.tg_posts_media_data.repository import TgPostsMediaDataRepository
from src.modules.tg_posts_media_data.schemas import TgPostsMediaDataModel
from src.modules.tg_posts_media_data.dto import AddTgPostsMediaData, UpdateTgPostsMediaData


async def get_all_telegram_posts_media_data() -> List[TgPostsMediaDataModel]:
    all_tg_posts_media_data = await TgPostsMediaDataRepository.get_all()
    return all_tg_posts_media_data


async def add_telegram_post_media_data(payload: AddTgPostsMediaData) -> TgPostsMediaDataModel:
    new_tg_post_media_data = await TgPostsMediaDataRepository.add_one(payload)

    if not new_tg_post_media_data:
        raise ValueError("Failed to create Telegram post media data")

    return new_tg_post_media_data


async def delete_telegram_post_media_data(media_data_id: UUID) -> None:
    await TgPostsMediaDataRepository.delete(media_data_id)


async def update_telegram_post_media_data(media_data_id: UUID, payload: UpdateTgPostsMediaData) -> TgPostsMediaDataModel:
    updated_tg_post_media_data = await TgPostsMediaDataRepository.update(media_data_id, payload)

    if not updated_tg_post_media_data:
        raise ValueError("Failed to update Telegram post media data")

    return updated_tg_post_media_data


async def get_telegram_post_media_data(media_data_id: UUID) -> TgPostsMediaDataModel:
    tg_post_media_data_item = await TgPostsMediaDataRepository.get_one_by_id(media_data_id)

    if not tg_post_media_data_item:
        raise ValueError("Telegram post media data not found")

    return tg_post_media_data_item


async def get_telegram_posts_media_data_by_media_id(media_id: UUID) -> List[TgPostsMediaDataModel]:
    tg_post_media_data_items = await TgPostsMediaDataRepository.get_all_by_media_id(media_id)
    return tg_post_media_data_items
