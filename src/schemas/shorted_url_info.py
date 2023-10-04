from pydantic import BaseModel, conint, ConfigDict

from src.schemas.base import BaseSchema


class ShortURLInfoReadCut(BaseModel):
    count: conint(ge=0)


class ShortURLInfo(BaseSchema):
    model_config = ConfigDict(from_attributes=True)
    host: str
    port: conint(ge=0)
    user_agent: str
    url_id: conint(ge=0)
    user_id: conint(ge=0) | None


class ShortURLInfoCreate(BaseModel):
    host: str
    port: conint(ge=0)
    user_agent: str
    url_id: conint(ge=0)
    user_id: conint(ge=0) | None


class ShortURLInfoRead(ShortURLInfo):
    pass
