import logging
import typing as T # noqa

from sqlalchemy import delete, update, insert
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.postgres.base import Base

Model = T.TypeVar("Model", Base, Base)


class RepoFactory:
    def __init__(self, model: T.Type[Model], session: async_sessionmaker) -> None:
        self.model = model
        self.session = session

    async def insert_one(self, **kwargs: T.Any) -> Model:
        model = kwargs.pop("model", None)
        if model is None:
            model = self.model
        async with self.session() as session:
            async with session.begin():
                try:
                    instance = model(**kwargs)
                    session.add(instance)
                    await session.flush()
                    await session.refresh(instance)
                    return instance
                except IntegrityError as e:
                    await session.rollback()
                    logging.error(f"Duplicate entry for {model.__name__}: {e}")
                    raise ValueError(f"Duplicate entry for {model.__name__}: {e}")
                except SQLAlchemyError as e:
                    await session.rollback()
                    logging.error(f"Error inserting {model.__name__}: {e}")
                    raise e

    async def insert_many(self, *args: T.Any) -> T.List[Model]:
        async with self.session() as session:
            async with session.begin():
                instances = await session.execute(insert(self.model).values(*args).returning(self.model))
                return list(instances.scalars().all())

    async def update(self, conditions: T.Dict[str, T.Any], values: T.Dict[str, T.Any]):
        async with self.session() as session:
            async with session.begin():
                stmt = update(self.model).where(
                    *[getattr(self.model, k) == v for k, v in conditions.items()]
                ).values(values).returning(self.model)
                try:
                    result = await session.execute(stmt)
                    await session.commit()
                    return result.scalars().all()
                except SQLAlchemyError as e:
                    await session.rollback()
                    logging.error(f"Error updating {self.model.__name__}: {e}")
                    raise

    async def delete_many(self, **conditions: T.Any) -> int:
        async with self.session() as session:
            async with session.begin():
                stmt = delete(self.model).where(*[getattr(self.model, k) == v for k, v in conditions.items()])
                try:
                    result = await session.execute(stmt)
                    await session.commit()
                    return result.rowcount  # noqa
                except SQLAlchemyError as e:
                    await session.rollback()
                    logging.error(f"Error deleting from {self.model.__name__}: {e}")
                    raise
