import os
from uuid import UUID
from PIL import Image
from fastapi import BackgroundTasks

from src.modules.embeddings.dto import GenerateImageDescriptionsPayload
from src.modules.embeddings.repository import EmbeddingsRepository
from src.shared.llm.image_description import ImageDescription
from src.config import STORAGE_FOLDER
from src.modules.embeddings.schemas import MediaForProcessing, MediaDataUpdate


async def process_media_item(media_item: MediaForProcessing, image_describer: ImageDescription):
    image_path = os.path.join(STORAGE_FOLDER, media_item.photos_path.lstrip('\\/'), media_item.media_name)

    if not os.path.exists(image_path):
        print(f"Warning: Image not found at {image_path}")
        return

    try:
        with Image.open(image_path) as img:
            description, desc_usage, desc_time = image_describer.get_description(img)
            tag, tag_usage, tag_time = image_describer.get_tag(img)
            structured_description, struct_desc_usage, struct_desc_time = image_describer.get_structured_description(img)

            update_data = MediaDataUpdate(
                media_id=media_item.media_id,
                description=description,
                tag=tag,
                structured_description=structured_description,
                desc_usage=desc_usage,
                tag_usage=tag_usage,
                struct_desc_usage=struct_desc_usage,
                desc_time=desc_time,
                tag_time=tag_time,
                struct_desc_time=struct_desc_time
            )
            await EmbeddingsRepository.update_media_data(update_data)
    except Exception as e:
        print(f"Warning: Error processing image {media_item.media_id}: {e}")



async def background_process_all(payload: GenerateImageDescriptionsPayload):
    image_describer = ImageDescription(model_name=payload.model_name)
    page_size = 10
    page = 0

    while True:
        media_to_process = []
        if payload.tg_export_id:
            media_to_process = await EmbeddingsRepository.get_media_for_processing_by_export_id(payload.tg_export_id, page_size, page * page_size)
        elif payload.tg_post_id:
            media_to_process = await EmbeddingsRepository.get_media_for_processing_by_post_id(payload.tg_post_id, page_size, page * page_size)

        if not media_to_process:
            break

        for media_item in media_to_process:
            await process_media_item(media_item, image_describer)

        if len(media_to_process) < page_size:
            break

        page += 1
    print("Finished background processing.")


async def background_process_single(media_id: UUID, model_name: str):
    image_describer = ImageDescription(model_name=model_name)
    media_item = await EmbeddingsRepository.get_media_for_processing_by_media_id(media_id)
    if media_item:
        await process_media_item(media_item, image_describer)
    print(f"Finished background processing for single media: {media_id}")


async def start_image_description_generation(
    payload: GenerateImageDescriptionsPayload,
    background_tasks: BackgroundTasks
):
    if payload.tg_media_id:
        background_tasks.add_task(background_process_single, payload.tg_media_id, payload.model_name)
    else:
        background_tasks.add_task(background_process_all, payload)
