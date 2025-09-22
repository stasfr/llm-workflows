import os
import aiosqlite
from uuid import UUID
from pathlib import Path
from src.config import STORAGE_FOLDER


def get_experiment_directory_path(experiment_id: UUID) -> Path:
    """Get the directory path for an experiment based on its UUID."""
    return Path(STORAGE_FOLDER) / str(experiment_id)


def get_experiment_sqlite_path(experiment_id: UUID) -> Path:
    """Get the SQLite database path for an experiment."""
    return get_experiment_directory_path(experiment_id) / "dataset.db"


async def create_experiment_directory_and_database(experiment_id: UUID) -> Path:
    """
    Create the experiment directory and initialize the SQLite database.

    Args:
        experiment_id: The UUID of the experiment

    Returns:
        Path to the created SQLite database file
    """
    # Create the experiment directory
    experiment_dir = get_experiment_directory_path(experiment_id)
    experiment_dir.mkdir(parents=True, exist_ok=True)

    # Create the SQLite database
    sqlite_path = get_experiment_sqlite_path(experiment_id)

    # Initialize the database with basic schema if needed
    async with aiosqlite.connect(sqlite_path) as db:
        # You can add any initial schema here if needed
        # For now, we'll just create an empty database
        await db.commit()

    return sqlite_path


async def cleanup_experiment_directory(experiment_id: UUID) -> None:
    """
    Clean up the experiment directory and all its contents.

    Args:
        experiment_id: The UUID of the experiment
    """
    experiment_dir = get_experiment_directory_path(experiment_id)
    if experiment_dir.exists():
        import shutil
        shutil.rmtree(experiment_dir)


def get_experiment_sqlite_path_str(experiment_id: UUID) -> str:
    """
    Get the SQLite database path as a string for an experiment.

    Args:
        experiment_id: The UUID of the experiment

    Returns:
        String path to the SQLite database file
    """
    return str(get_experiment_sqlite_path(experiment_id))
