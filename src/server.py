from fastapi import FastAPI

from src.router import router as api_router

app = FastAPI(
    title="LLM Workflows API",
    description="API for managing LLM workflows",
    version="0.1.0",
)

app.include_router(api_router)
