import logging

from fastapi import (
    APIRouter,
    Depends,
    Header,
    HTTPException,
    Request,
    Response,
    status,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.db import get_session
from src.schemas.shorted_url_info import (
   ShortURLInfoCreate,
   ShortURLInfoRead,
   ShortURLInfoReadCut,
)
from src.schemas.shorted_url import (
    ShortedURLBatchRead,
    ShortedURLCreate,
    ShortedURLRead,
    ShortedURLUpdate,
)
from src.services.services import short_url_service, url_info_service
from src.services.shorter import generate_short_url

router = APIRouter()
logger = logging.getLogger(__name__)


def host_extractor(request: Request) -> str:
    return request.client.host


def port_extractor(request: Request) -> int:
    return request.client.port


async def get_short_url(
    *,
    db: AsyncSession = Depends(get_session),
    id: int,
) -> ShortedURLRead:
    url_object = await short_url_service.get(db=db, id=id)
    if url_object is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="URL is not found"
        )
    return url_object


async def log_url_use(
    *,
    db: AsyncSession = Depends(get_session),
    host: str = Depends(host_extractor),
    port: int = Depends(port_extractor),
    user_agent: str | None = Header(default=None),
    short_url: ShortedURLRead = Depends(get_short_url),
) -> ShortURLInfoRead:
    url_use_data = ShortURLInfoCreate.parse_obj(
        {
            "host": host,
            "port": port,
            "user_agent": user_agent or "unknown",
            "url_id": short_url.id,
            "user_id": None,
        }
    )
    db_object = await url_info_service.create(db=db, object_in=url_use_data)
    info = ShortURLInfoRead.from_orm(db_object)
    logger.info(f"Logged URL use: {info}")
    return info


@router.post("/shorten", response_model=list[ShortedURLBatchRead])
async def bulk_create_short_url(
    *,
    db: AsyncSession = Depends(get_session),
    urls: list[ShortedURLCreate],
) -> list[ShortedURLBatchRead]:
    objects_in = [
        {
            "value": generate_short_url(str(url.original_url)),
            "original": str(url.original_url),
        }
        for url in urls
    ]
    db_objects = await short_url_service.bulk_create(
        db=db, objects_in=objects_in
    )
    urls_out = [
        ShortedURLBatchRead(short_id=obj.id, short_url=obj.value)
        for obj in db_objects
    ]
    return urls_out


@router.get("/{id}", status_code=status.HTTP_307_TEMPORARY_REDIRECT)
async def read_short_url(
    *,
    short_url: ShortedURLRead = Depends(get_short_url),
    use: ShortURLInfoRead = Depends(log_url_use),
) -> Response:
    """Get URL by ID & log use"""
    if short_url.deleted:
        return Response(status_code=status.HTTP_410_GONE)
    logger.info(f"Redirecting to: {short_url.original}")
    headers = {"Location": short_url.original}
    return Response(
        content="",
        status_code=status.HTTP_307_TEMPORARY_REDIRECT,
        headers=headers,
    )


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def mark_deleted_short_url(
    *,
    db: AsyncSession = Depends(get_session),
    short_url: ShortedURLRead = Depends(get_short_url),
) -> None:
    await short_url_service.update(
        db=db, db_object=short_url, object_in=ShortedURLUpdate(deleted=True)
    )
    logger.info(f"Mark {short_url.value} ({short_url.original}) as deleted")


@router.get(
    "/{id}/status", response_model=list[ShortURLInfoRead] | ShortURLInfoReadCut
)
async def read_short_url_info_history(
    *,
    db: AsyncSession = Depends(get_session),
    id: int,
    full_info: bool | None = None,
    offset: int = 0,
    max_result: int = 10,
) -> list[ShortURLInfoRead] | ShortURLInfoReadCut:
    if not full_info:
        url_uses_count = await url_info_service.count(
            db, filter=dict(url_id=id)
        )
        return ShortURLInfoReadCut(count=url_uses_count)
    url_uses = await url_info_service.get_multi(
        db=db, filter=dict(url_id=id), skip=offset, limit=max_result
    )
    return url_uses


@router.post(
    "/", status_code=status.HTTP_201_CREATED, response_model=ShortedURLRead
)
async def create_short_url(
    *,
    db: AsyncSession = Depends(get_session),
    url: ShortedURLCreate,
) -> ShortedURLRead:
    original = str(url.original_url)
    urls_count = await short_url_service.count(db, filter={"original": original})
    if urls_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="URL already exists",
        )
    data = {
        "value": generate_short_url(original),
        "original": original,
    }

    url_object = await short_url_service.create(db=db, object_in=data)

    return ShortedURLRead.from_orm(url_object)
