from fastapi import APIRouter

from .blacklist import router as blacklist_router
from .db import router as db_router
from .short_url import router as short_url_router

api_router = APIRouter()

api_router.include_router(blacklist_router, prefix="")
api_router.include_router(db_router, prefix="")
api_router.include_router(short_url_router, prefix="")