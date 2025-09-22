from uuid import UUID
from typing import List, Annotated

from fastapi import APIRouter, Body, Path

from src.modules.experiments.services import (
    get_all_experiments,
    add_experiment,
    update_experiment,
    delete_experiment,
    get_experiment,
    get_experiments_by_tg_export
)
from src.modules.experiments.schemas import ExperimentModel
from src.modules.experiments.dto import AddExperiment, UpdateExperiment
from src.schemas import PlainDataResponse, ApiResponse


router = APIRouter(
    prefix="/experiments",
    tags=["Experiments"],
)


@router.get("/", description="Get all experiments.")
async def get_all_experiments_handler() -> ApiResponse[List[ExperimentModel] | PlainDataResponse]:
    try:
        all_experiments = await get_all_experiments()
        return ApiResponse(data=all_experiments)
    except Exception as e:
        return ApiResponse(data=PlainDataResponse(error=str(e)))


@router.post("/", description="Add a new experiment.")
async def add_experiment_handler(
    payload: Annotated[AddExperiment, Body(
        description="Experiment creation payload")]
) -> ApiResponse[ExperimentModel] | ApiResponse[PlainDataResponse]:
    try:
        new_experiment = await add_experiment(payload)
        return ApiResponse(data=new_experiment)
    except Exception as e:
        return ApiResponse(data=PlainDataResponse(error=str(e)))


@router.delete("/{experiment_id}", description="Delete an experiment.")
async def delete_experiment_handler(
    experiment_id: Annotated[UUID, Path(
        title="Id of experiment (UUID v4)",
        description="Id of the experiment to be deleted",
        examples=["3fa85f64-5717-4562-b3fc-2c963f66afa6"]
    )]
) -> ApiResponse[PlainDataResponse]:
    try:
        await delete_experiment(experiment_id)
        return ApiResponse(data=PlainDataResponse(message="Done!"))
    except Exception as e:
        return ApiResponse(data=PlainDataResponse(error=str(e)))


@router.put("/{experiment_id}", description="Update an experiment.")
async def update_experiment_handler(
    experiment_id: Annotated[UUID, Path(
        title="Id of experiment (UUID v4)",
        description="Id of the experiment to be updated",
        examples=["3fa85f64-5717-4562-b3fc-2c963f66afa6"]
    )],
    payload: Annotated[UpdateExperiment, Body(
        description="Experiment update payload")]
) -> ApiResponse[ExperimentModel] | ApiResponse[PlainDataResponse]:
    try:
        updated_experiment = await update_experiment(experiment_id, payload)
        return ApiResponse(data=updated_experiment)
    except Exception as e:
        return ApiResponse(data=PlainDataResponse(error=str(e)))


@router.get("/{experiment_id}", description="Get an experiment by ID.")
async def get_experiment_handler(
    experiment_id: Annotated[UUID, Path(
        title="Id of experiment (UUID v4)",
        description="Id of the experiment to be retrieved",
        examples=["3fa85f64-5717-4562-b3fc-2c963f66afa6"]
    )]
) -> ApiResponse[ExperimentModel | PlainDataResponse]:
    try:
        experiment_item = await get_experiment(experiment_id)
        return ApiResponse(data=experiment_item)
    except Exception as e:
        return ApiResponse(data=PlainDataResponse(error=str(e)))


@router.get("/by-tg-export/{tg_export_id}", description="Get all experiments by Telegram export ID.")
async def get_experiments_by_tg_export_handler(
    tg_export_id: Annotated[UUID, Path(
        title="Id of Telegram export (UUID v4)",
        description="Id of the Telegram export to get experiments for",
        examples=["3fa85f64-5717-4562-b3fc-2c963f66afa6"]
    )]
) -> ApiResponse[List[ExperimentModel] | PlainDataResponse]:
    try:
        experiments = await get_experiments_by_tg_export(tg_export_id)
        return ApiResponse(data=experiments)
    except Exception as e:
        return ApiResponse(data=PlainDataResponse(error=str(e)))
