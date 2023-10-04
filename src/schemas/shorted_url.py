from pydantic import BaseModel, HttpUrl, conint, ConfigDict

from src.schemas.base import BaseSchema


class ShortedURL(BaseSchema):
    model_config = ConfigDict(from_attributes=True)
    value: HttpUrl
    original: HttpUrl
    deleted: bool


class ShortedURLRead(ShortedURL):
    pass


class ShortedURLUpdate(BaseModel):
    deleted: bool


class ShortedURLCreate(BaseModel):
    original_url: HttpUrl


class ShortedURLBatchRead(BaseModel):
    short_id: conint(ge=0)
    short_url: HttpUrl
