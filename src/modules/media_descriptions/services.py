import os
from uuid import UUID
from PIL import Image
from fastapi import BackgroundTasks

from src.modules.media_descriptions.dto import GenerateImageDescriptionsPayload
from src.modules.media_descriptions.repository import MediaDescriptionsRepository
from src.modules.media_descriptions.schemas import MediaForProcessing, MediaDataUpdate
from src.shared.llm.image_description import ImageDescription
from src.modules.jobs.services import add_job, update_job_status
from src.modules.jobs.schemas import JobStatus, AddJob, UpdateJobStatus
from src.config import STORAGE_FOLDER
from src.modules.tg_exports.repository import TgExportsRepository


async def process_media_item(image_base_path: str, media_item: MediaForProcessing, image_describer: ImageDescription, experiment_id: UUID):
    image_path = os.path.join(image_base_path, media_item.media_name)

    if not os.path.exists(image_path):
        print(f"Warning: Image not found at {image_path}")
        return

    try:
        with Image.open(image_path) as img:
            description, desc_usage, desc_time = image_describer.get_description(
                img)
            tag, tag_usage, tag_time = image_describer.get_tag(img)
            structured_description, struct_desc_usage, struct_desc_time = image_describer.get_structured_description(
                img)

            update_data = MediaDataUpdate(
                media_data_id=media_item.media_data_id,
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
            await MediaDescriptionsRepository.update_media_data(experiment_id, update_data)
    except Exception as e:
        print(f"Warning: Error processing image {media_item.media_id}: {e}")


async def background_process_by_export(experiment_id: UUID, export_id: UUID, model_name: str, job_id: UUID):
    # Update job status to in progress if job_id is provided
    if job_id:
        await update_job_status(job_id, UpdateJobStatus(status=JobStatus.IN_PROGRESS))

    image_describer = ImageDescription(model_name=model_name)
    tg_export = await TgExportsRepository.get_one_by_id(export_id)
    if not tg_export:
        raise ValueError(f"Telegram export with ID {export_id} not found")
    image_base_path = os.path.join(
        STORAGE_FOLDER, tg_export.photos_path.lstrip('\\/'))
    page_size = 10
    page = 0
    while True:
        media_to_process = await MediaDescriptionsRepository.get_media_for_processing_by_export_id(experiment_id, export_id, page_size, page * page_size)
        if not media_to_process:
            break
        for media_item in media_to_process:
            await process_media_item(image_base_path, media_item, image_describer, experiment_id)
        if len(media_to_process) < page_size:
            break
        page += 1

    # Update job status to completed if job_id is provided
    if job_id:
        await update_job_status(job_id, UpdateJobStatus(status=JobStatus.COMPLETED))

    print(f"Finished background processing for export: {export_id}")


async def background_process_by_post(post_id: UUID, model_name: str, job_id: UUID):
    # Update job status to in progress if job_id is provided
    if job_id:
        await update_job_status(job_id, UpdateJobStatus(status=JobStatus.IN_PROGRESS))

    # Deprecated in new flow; keeping stub for compatibility if referenced elsewhere
    return

    # Update job status to completed if job_id is provided
    if job_id:
        await update_job_status(job_id, UpdateJobStatus(status=JobStatus.COMPLETED))

    print(f"Finished background processing for post: {post_id}")


async def background_process_single(media_id: UUID, model_name: str, job_id: UUID):
    # Update job status to in progress if job_id is provided
    if job_id:
        await update_job_status(job_id, UpdateJobStatus(status=JobStatus.IN_PROGRESS))

    # Deprecated in new flow; keeping stub for compatibility if referenced elsewhere
    return

    # Update job status to completed if job_id is provided
    if job_id:
        await update_job_status(job_id, UpdateJobStatus(status=JobStatus.COMPLETED))

    print(f"Finished background processing for single media: {media_id}")


async def start_image_description_generation_by_export(
    payload: GenerateImageDescriptionsPayload,
    background_tasks: BackgroundTasks
):
    # Create a job for tracking this background process
    job_metadata = f"Process media for export with {payload.tg_export_id}"
    job = await add_job(AddJob(status=JobStatus.PENDING, metadata=job_metadata))

    background_tasks.add_task(
        background_process_by_export, payload.experiment_id, payload.tg_export_id, payload.model_name, job.id)
