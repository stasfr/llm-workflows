from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.router import router as api_router


app = FastAPI(
    title="LLM Workflows API",
    description="API for managing LLM workflows",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
