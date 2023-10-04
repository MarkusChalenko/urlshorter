import factory

from src.db.db import async_session
from src.models.models import BlacklistedClient, ShortedURL, ShortedURLInfo


class AsyncModelFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        abstract = True

    @classmethod
    def _save(cls, model_class, session, args, kwargs):
        async def create_coro(*args, **kwargs):
            db_object = model_class(*args, **kwargs)
            async with session() as s:
                s.add(db_object)
                await s.commit()
                await s.refresh(db_object)
            return db_object

        return create_coro(*args, **kwargs)


class ShortedURLFactory(AsyncModelFactory):
    value = factory.LazyAttribute(
        lambda obj: f"{obj.original}not-really-shortened/"
    )
    original = factory.Faker("url")
    created_at = factory.Faker("date_time")
    deleted = False

    class Meta:
        model = ShortedURL
        sqlalchemy_session = async_session


class ShortedURLInfoFactory(AsyncModelFactory):
    host = factory.Faker("ipv4")
    port = factory.Faker("random_int", min=0, max=9999)
    user_agent = factory.Faker("word")
    url_id = factory.SubFactory(ShortedURLFactory)

    class Meta:
        model = ShortedURLInfo
        sqlalchemy_session = async_session


class BlacklistClientFactory(AsyncModelFactory):
    host = factory.Faker("ipv4")
    until = factory.Faker("date_time")

    class Meta:
        model = BlacklistedClient
        sqlalchemy_session = async_session