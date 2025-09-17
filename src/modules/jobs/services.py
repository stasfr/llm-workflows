from typing import List
from uuid import UUID

from src.modules.jobs.repository import JobsRepository
from src.modules.jobs.schemas import JobModel
from src.modules.jobs.schemas import AddJob, UpdateJobStatus


async def get_all_jobs() -> List[JobModel]:
    jobs = await JobsRepository.get_all()
    return jobs

async def add_job(payload: AddJob) -> JobModel:
    new_job = await JobsRepository.add_one(payload)

    if not new_job:
        raise ValueError("Failed to create job")

    return new_job

async def delete_job(job_id: UUID) -> None:
    await JobsRepository.delete(job_id)

async def update_job_status(job_id: UUID, payload: UpdateJobStatus) -> JobModel:
    updated_job = await JobsRepository.update_status(job_id, payload)

    if not updated_job:
        raise ValueError("Failed to update job")

    return updated_job

async def get_job(job_id: UUID) -> JobModel:
    job_item = await JobsRepository.get_one_by_id(job_id)

    if not job_item:
        raise ValueError("Job not found")

    return job_item
