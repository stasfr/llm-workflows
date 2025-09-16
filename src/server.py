from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.router import router as api_router
from src.utils.db_health import check_psql_connection, check_milvus_connection


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Checking database connections on startup...")
    try:
        await check_psql_connection()
        await check_milvus_connection()
        print("Database connections are healthy.")
    except Exception as e:
        print(f"Database connection check failed: {e}")
        # Raising an exception during startup will prevent FastAPI from starting.
        raise
    yield
    print("Server is shutting down.")


app = FastAPI(
    title="LLM Workflows API",
    description="API for managing LLM workflows",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
