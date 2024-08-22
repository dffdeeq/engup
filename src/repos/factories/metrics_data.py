import typing as T  # noqa
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.postgres.models.metrics_data import MetricsData
from src.repos.factory import RepoFactory


class MetricsDataRepo(RepoFactory):
    def __init__(self, model: T.Type[MetricsData], session: async_sessionmaker):
        super().__init__(model, session)

    async def get_metrics_data(self, metrics_uuid: uuid.UUID) -> T.Optional[MetricsData]:
        async with self.session() as session:
            query = select(self.model).where(self.model.uuid == metrics_uuid)
            result = await session.execute(query)
            return result.scalar_one_or_none()

    async def create_metrics_data(self, metrics_uuid: uuid.UUID, metrics_string: str) -> MetricsData:
        instance = await self.insert_one(uuid=metrics_uuid, metrics_string=metrics_string)
        return instance
