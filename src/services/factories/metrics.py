import typing as T  # noqa
import uuid

from sqlalchemy.ext.asyncio import async_sessionmaker

from src.libs.adapter import Adapter
from src.postgres.models.metrics_data import MetricsData
from src.repos.factories.metrics_data import MetricsDataRepo
from src.services.factory import ServiceFactory
from src.settings import Settings


class MetricsService(ServiceFactory):
    def __init__(self, repo: MetricsDataRepo, adapter: Adapter, session: async_sessionmaker, settings: Settings):
        super().__init__(repo, adapter, session, settings)
        self.repo = repo

    async def get_metrics_data(self, metrics_uuid: uuid.UUID) -> T.Optional[MetricsData]:
        return await self.repo.get_metrics_data(metrics_uuid)

    async def create_metrics_data(self, metrics_uuid: uuid.UUID, metrics_string: str) -> MetricsData:
        return await self.repo.create_metrics_data(metrics_uuid, metrics_string)
