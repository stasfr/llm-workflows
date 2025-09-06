from fastapi import FastAPI
from pydantic import BaseModel

from typing import Optional

from parsers.parse_raw_telegram_data import parse_raw_telegram_data
from db.db import init_db, init_experiments_db


app = FastAPI(
    title="LLM Workflows API",
    description="API for managing LLM workflows",
    version="0.1.0",
)

class ApiResult(BaseModel):
    result: str
    error: Optional[str] = None

class Project(BaseModel):
    name: str
    snapshot: str

@app.post("/init_db", tags=["Database"], description="Initialize the main database for a project.")
def init_db_handler(
    project: Project,
) -> ApiResult:
    db_name = f"{project.name}_{project.snapshot}"
    try:
        init_db(db_name)
    except Exception as e:
        return ApiResult(result="", error=str(e))
    return ApiResult(result=f"Database {db_name} initialized successfully", error=None)

@app.post("/init_experiments_db", tags=["Database"], description="Initialize the database for experiments.")
def init_experiments_db_handler() -> ApiResult:
    try:
        init_experiments_db()
    except Exception as e:
        return ApiResult(result="", error=str(e))
    return ApiResult(result="Experiment Database initialized successfully", error=None)

@app.post("/parse_telegram_data", tags=["Data Processing"], description="Parses raw data from Telegram for a project.")
def parse_telegram_data_handler(
    project: Project,
) -> ApiResult:
    try:
        parse_raw_telegram_data(project_name=project.name, project_snapshot=project.snapshot)
        return ApiResult(result=f"Data for project {project.name}_{project.snapshot} parsed successfully", error=None)
    except Exception as e:
        return ApiResult(result="", error=str(e))
