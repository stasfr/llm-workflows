from typing import List
from uuid import UUID

from src.modules.experiments.repository import ExperimentsRepository
from src.modules.experiments.schemas import ExperimentModel
from src.modules.experiments.dto import AddExperiment, UpdateExperiment


async def get_all_experiments() -> List[ExperimentModel]:
    all_experiments = await ExperimentsRepository.get_all()
    return all_experiments


async def add_experiment(payload: AddExperiment) -> ExperimentModel:
    new_experiment = await ExperimentsRepository.add_one(payload)

    if not new_experiment:
        raise ValueError("Failed to create experiment")

    return new_experiment


async def delete_experiment(experiment_id: UUID) -> None:
    await ExperimentsRepository.delete(experiment_id)


async def update_experiment(experiment_id: UUID, payload: UpdateExperiment) -> ExperimentModel:
    updated_experiment = await ExperimentsRepository.update(experiment_id, payload)

    if not updated_experiment:
        raise ValueError("Failed to update experiment")

    return updated_experiment


async def get_experiment(experiment_id: UUID) -> ExperimentModel:
    experiment_item = await ExperimentsRepository.get_one_by_id(experiment_id)

    if not experiment_item:
        raise ValueError("Experiment not found")

    return experiment_item


async def get_experiments_by_tg_export(tg_export_id: UUID) -> List[ExperimentModel]:
    experiments = await ExperimentsRepository.get_by_tg_export_id(tg_export_id)
    return experiments
