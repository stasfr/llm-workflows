from fastapi import FastAPI

# from contextlib import asynccontextmanager

from src.router import router as api_router
# from src.database import create_tables
# import src.models


# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     await create_tables()
#     yield


app = FastAPI(
    # lifespan=lifespan,
    title="LLM Workflows API",
    description="API for managing LLM workflows",
    version="0.1.0",
)


app.include_router(api_router)
