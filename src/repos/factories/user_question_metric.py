import typing as T # noqa

from sqlalchemy.ext.asyncio import async_sessionmaker

from src.postgres.models.tg_user_question import TgUserQuestionMetric
from src.repos.factory import RepoFactory


class TgUserQuestionMetricRepo(RepoFactory):
    def __init__(self, model: T.Type[TgUserQuestionMetric], session: async_sessionmaker):
        super().__init__(model, session)

    async def create(self, uq_id: int, metric_id: str, value: float, details: str = None):
        await self.insert_one(uq_id=uq_id, metric_id=metric_id, value=value, details=details)
