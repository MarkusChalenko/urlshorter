import logging
from typing import Any, Generic, Type, TypeVar

from pydantic import BaseModel
from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import functions

from src.db.db import Base

logger = logging.getLogger(__name__)


class Repository:
    def get(self, *args, **kwargs):
        raise NotImplementedError

    def get_multi(self, *args, **kwargs):
        raise NotImplementedError

    def create(self, *args, **kwargs):
        raise NotImplementedError

    def update(self, *args, **kwargs):
        raise NotImplementedError

    def delete(self, *args, **kwargs):
        raise NotImplementedError


ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class RepositoryDB(
    Repository, Generic[ModelType, CreateSchemaType, UpdateSchemaType]
):
    def __init__(self, model: Type[ModelType]):
        self._model = model

    async def get(self, db: AsyncSession, id: Any) -> ModelType | None:
        statement = select(self._model).where(self._model.id == id)
        results = await db.execute(statement=statement)
        return results.scalar_one_or_none()

    async def get_multi(
        self,
        db: AsyncSession,
        *,
        filter: dict[str, Any] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[ModelType]:
        filter = filter or {}
        statement = (
            select(self._model).filter_by(**filter).offset(skip).limit(limit)
        )
        results = await db.execute(statement=statement)
        return results.scalars().all()

    async def create(
        self, db: AsyncSession, *, object_in: CreateSchemaType | dict[str, Any]
    ) -> ModelType:
        db_object = self._model(**dict(object_in))
        db.add(db_object)
        await db.commit()
        await db.refresh(db_object)
        return db_object

    async def bulk_create(
        self,
        db: AsyncSession,
        objects_in: list[CreateSchemaType] | list[dict[str, Any]],
    ) -> list[ModelType]:
        """
        Batched INSERT statements via the ORM in "bulk",
        returning new model objects
        """
        statement = insert(self._model).returning(self._model)
        results = await db.scalars(
            statement=statement,
            params=[{**dict(object_in)} for object_in in objects_in],
        )
        await db.commit()
        return results.all()

    async def update(
        self,
        db: AsyncSession,
        *,
        db_object: ModelType,
        object_in: UpdateSchemaType | dict[str, Any],
    ) -> ModelType:
        obj_in_data = dict(object_in)
        obj_in_data.pop("id", None)
        statement = (
            update(self._model)
            .filter_by(id=db_object.id)
            .values(**obj_in_data)
        )
        await db.execute(statement=statement)
        await db.commit()
        await db.refresh(db_object)
        return db_object

    async def delete(self, db: AsyncSession, *, id: int | None = None) -> None:
        filter = {"id": id} if id else {}
        statement = delete(self._model).filter_by(**filter)
        await db.execute(statement=statement)
        await db.commit()

    async def count(
        self, db: AsyncSession, *, filter: dict[str, Any] = None
    ) -> int:
        filter = filter or {}
        statement = (
            select(self._model)
            .filter_by(**filter)
            .with_only_columns(*[functions.count()])
        )
        result = await db.execute(statement=statement)
        return result.scalar()

    async def get_current_time(self, db: AsyncSession) -> str:
        statement = select(functions.now())
        try:
            result = await db.execute(statement=statement)
            return result.scalar()
        except ConnectionRefusedError as error:
            logger.error(error)
            return ""