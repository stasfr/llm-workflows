from fastapi import APIRouter

from src.modules.parsers.router import router as parsers_router


router = APIRouter(
    prefix="/api",
)

router.include_router(parsers_router)
