from pydantic import Field, SecretStr

from src.schemas.base import BaseSchema


class User(BaseSchema):
    username: str
    password: SecretStr = Field(exclude=True)
