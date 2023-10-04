from datetime import datetime

from pydantic import BaseModel, conint


class BaseSchema(BaseModel):
    id: conint(ge=0)
    created_at: datetime

    class Config:
        orm_mode = True
