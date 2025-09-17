from fastapi import APIRouter

from src.modules.db_psql.router import router as db_psql_router
from src.modules.db_milvus.router import router as db_milvus_router
from src.modules.tg_exports.router import router as tg_exports_router
from src.modules.parsers.router import router as parsers_router
from src.modules.tg_posts.router import router as tg_posts_router
from src.modules.tg_posts_media.router import router as tg_posts_media_router
from src.modules.tg_posts_media_data.router import router as tg_posts_media_data_router
from src.modules.media_descriptions.router import router as media_descriptions_router

router = APIRouter(
    prefix="/api",
)

router.include_router(db_psql_router)
router.include_router(db_milvus_router)
router.include_router(tg_exports_router)
router.include_router(parsers_router)
router.include_router(tg_posts_router)
router.include_router(tg_posts_media_router)
router.include_router(tg_posts_media_data_router)
router.include_router(media_descriptions_router)
