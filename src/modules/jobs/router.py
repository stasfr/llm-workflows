from uuid import UUID
from typing import List, Annotated

from fastapi import APIRouter, Body, Path

from src.modules.jobs.services import (
    get_all_jobs,
    add_job,
    update_job_status,
    delete_job,
    get_job
)
from src.modules.jobs.schemas import JobModel, AddJob, UpdateJobStatus
from src.schemas import PlainDataResponse, ApiResponse


router = APIRouter(
    prefix="/jobs",
    tags=["Jobs"],
)


@router.get("/", description="Get all jobs.")
async def get_all_jobs_handler() -> ApiResponse[List[JobModel] | PlainDataResponse]:
    try:
        jobs = await get_all_jobs()
        return ApiResponse(data=jobs)
    except Exception as e:
        return ApiResponse(data=PlainDataResponse(error=str(e)))


@router.post("/", description="Add a new job.")
async def add_job_handler(
    payload: Annotated[AddJob, Body(description="Job creation payload")]
) -> ApiResponse[JobModel] | ApiResponse[PlainDataResponse]:
    try:
        new_job = await add_job(payload)
        return ApiResponse(data=new_job)
    except Exception as e:
        return ApiResponse(data=PlainDataResponse(error=str(e)))


@router.delete("/{job_id}", description="Delete a job.")
async def delete_job_handler(
    job_id: Annotated[UUID, Path(
        title="Id of job (UUID v4)",
        description="Id of the job to be deleted",
        examples=["3fa85f64-5717-4562-b3fc-2c963f66afa6"]
    )]
) -> ApiResponse[PlainDataResponse]:
    try:
        await delete_job(job_id)
        return ApiResponse(data=PlainDataResponse(message="Done!"))
    except Exception as e:
        return ApiResponse(data=PlainDataResponse(error=str(e)))


@router.put("/{job_id}/status", description="Update a job status.")
async def update_job_status_handler(
    job_id: Annotated[UUID, Path(
        title="Id of job (UUID v4)",
        description="Id of the job to be updated",
        examples=["3fa85f64-5717-4562-b3fc-2c963f66afa6"]
    )],
    payload: Annotated[UpdateJobStatus, Body(
        description="Job status update payload")]
) -> ApiResponse[JobModel] | ApiResponse[PlainDataResponse]:
    try:
        updated_job = await update_job_status(job_id, payload)
        return ApiResponse(data=updated_job)
    except Exception as e:
        return ApiResponse(data=PlainDataResponse(error=str(e)))


@router.get("/{job_id}", description="Get a job by ID.")
async def get_job_handler(
    job_id: Annotated[UUID, Path(
        title="Id of job (UUID v4)",
        description="Id of the job to be retrieved",
        examples=["3fa85f64-5717-4562-b3fc-2c963f66afa6"]
    )]
) -> ApiResponse[JobModel | PlainDataResponse]:
    try:
        job_item = await get_job(job_id)
        return ApiResponse(data=job_item)
    except Exception as e:
        return ApiResponse(data=PlainDataResponse(error=str(e)))
