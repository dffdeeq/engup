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
        model = kwargs.pop('model', self.model)
        async with self.session() as session:
            async with session.begin():
                instance = model(**kwargs)
                session.add(instance)
                try:
                    await session.flush()
                    await session.refresh(instance)
                    return instance
                except IntegrityError:
                    await session.rollback()
                    logging.info(
                        f"Duplicate entry for {model.__name__} "
                        f"(user_id={kwargs.get('user_id')} question_id={kwargs.get('question_id')})"
                    )
                except SQLAlchemyError as e:
                    await session.rollback()
                    logging.error(f"Error inserting {model.__name__}: {e}")
                    raise

    async def insert_many(self, *args: T.Any) -> T.List[Model]:
        async with self.session() as session:
            async with session.begin():
                instances = await session.execute(insert(self.model).values(*args).returning(self.model))
                return list(instances.scalars().all())

    async def update_many(self, conditions: T.Dict[str, T.Any], values: T.Dict[str, T.Any], **kwargs) -> int:
        model = kwargs.pop('model', self.model)
        async with self.session() as session:
            async with session.begin():
                stmt = update(model).where(
                    *[getattr(model, k) == v for k, v in conditions.items()]
                ).values(values)
                try:
                    result = await session.execute(stmt)
                    await session.commit()
                    return result.rowcount  # noqa
                except SQLAlchemyError as e:
                    await session.rollback()
                    logging.error(f"Error updating {model.__name__}: {e}")
                    raise

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
