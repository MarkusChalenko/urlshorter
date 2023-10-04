import logging

from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from src.db.db import get_session
from src.services.services import blacklist_service

logger = logging.getLogger(__name__)


class BlacklistMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        async for db in get_session():
            blacklisted_times = await blacklist_service.count(
                db=db, filter=dict(host=request.client.host)
            )
        if blacklisted_times > 0:
            logger.info(
                "Blacklisted client %s connection attempt", request.client.host
            )
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"detail": "You`ve been temporary blacklisted"},
            )
        return await call_next(request)