import os
from typing import AsyncGenerator

import pytest
from _pytest.monkeypatch import MonkeyPatch
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncEngine,
    AsyncSession,
    create_async_engine,
)
from sqlalchemy.orm import sessionmaker

from src.db.db import Base
from src.main import app


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture(scope="session")
async def engine() -> AsyncEngine:
    engine = create_async_engine(
        os.getenv("PROJECT_DB"),
        echo=True,
        connect_args={"check_same_thread": False},
    )
    try:
        yield engine
    finally:
        await engine.dispose()


@pytest.fixture(scope="session", autouse=True)
async def test_db(engine: AsyncEngine) -> None:
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
        yield
        await connection.run_sync(Base.metadata.drop_all)


@pytest.fixture()
async def db_connection(
    engine: AsyncEngine,
) -> AsyncGenerator[AsyncConnection, None]:
    async with engine.connect() as connection:
        yield connection


@pytest.fixture(autouse=True)
async def session(
    db_connection: AsyncConnection, monkeypatch: MonkeyPatch
) -> AsyncGenerator[AsyncSession, None]:
    session_maker = sessionmaker(
        bind=db_connection, class_=AsyncSession, expire_on_commit=False
    )
    monkeypatch.setattr("db.db.async_session", session_maker)

    async with session_maker() as session:
        yield session


@pytest.fixture
async def api_client(session) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
