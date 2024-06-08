import logging
import typing as T # noqa

from sqlalchemy import delete, update, select, insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.postgres.base import Base

Model = T.TypeVar("Model", Base, Base)


class RepoFactory:
    def __init__(self, model: T.Type[Model], session: async_sessionmaker) -> None:
        self.model = model
        self.session = session

    async def insert_one(self, **kwargs: T.Any) -> Model:
        async with self.session() as session:
            async with session.begin():
                instance = self.model(**kwargs)
                session.add(instance)
                try:
                    await session.flush()
                    await session.refresh(instance)
                    return instance
                except SQLAlchemyError as e:
                    await session.rollback()
                    logging.error(f"Error inserting {self.model.__name__}: {e}")
                    raise

    async def insert_many(self, *args: T.Any) -> T.List[Model]:
        async with self.session() as session:
            async with session.begin():
                instances = await session.execute(insert(self.model).values(*args).returning(self.model))
                return instances.scalars().all()

    async def update_many(self, conditions: T.Dict[str, T.Any], values: T.Dict[str, T.Any]) -> int:
        async with (self.session() as session):
            async with session.begin():
                stmt = update(self.model).where(
                    *[getattr(self.model, k) == v for k, v in conditions.items()]
                ).values(values)
                try:
                    result = await session.execute(stmt)
                    await session.commit()
                    return result.rowcount()
                except SQLAlchemyError as e:
                    await session.rollback()
                    logging.error(f"Error updating {self.model.__name__}: {e}")
                    raise

    async def get_one(self, **conditions: T.Any) -> T.Optional[Model]:
        async with self.session() as session:
            async with session.begin():
                stmt = select(self.model).where(*[getattr(self.model, k) == v for k, v in conditions.items()])
                result = await session.execute(stmt)
                return result.scalars().first()

    async def get_many(self, **conditions: T.Any) -> T.List[Model]:
        async with self.session() as session:
            async with session.begin():
                stmt = select(self.model).where(*[getattr(self.model, k) == v for k, v in conditions.items()])
                result = await session.execute(stmt)
                return result.scalars().all()

    async def delete_many(self, **conditions: T.Any) -> int:
        async with self.session() as session:
            async with session.begin():
                stmt = delete(self.model).where(*[getattr(self.model, k) == v for k, v in conditions.items()])
                try:
                    result = await session.execute(stmt)
                    await session.commit()
                    return result.rowcount()
                except SQLAlchemyError as e:
                    await session.rollback()
                    logging.error(f"Error deleting from {self.model.__name__}: {e}")
                    raise
