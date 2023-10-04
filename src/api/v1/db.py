import logging

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.db import get_session
from src.schemas.status import Status
from src.services.services import url_info_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/ping", response_model=Status)
async def ping_db(*, db: AsyncSession = Depends(get_session)) -> Status:
    time = await url_info_service.get_current_time(db=db)
    if time:
        message = f"Connection established. Database time: {time}"
    else:
        message = "Database is not available"
    return Status(message=message)