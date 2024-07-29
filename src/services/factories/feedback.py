import typing as T  # noqa

from sqlalchemy.ext.asyncio import async_sessionmaker

from src.libs.adapter import Adapter
from src.postgres.models.poll_feedback import PollFeedback
from src.repos.factories.feedback import FeedbackRepo
from src.services.factory import ServiceFactory
from src.settings import Settings


class FeedbackService(ServiceFactory):
    def __init__(self, repo: FeedbackRepo, adapter: Adapter, session: async_sessionmaker, settings: Settings) -> None:
        super().__init__(repo, adapter, session, settings)
        self.repo = repo

    async def save_user_poll_feedback(self, user_id, feedback_dict: T.Dict) -> PollFeedback:
        return await self.repo.create_user_poll_feedback(user_id, feedback_dict)

    async def user_can_get_free_points(self, user_id: int) -> bool:
        return True if await self.repo.get_user_poll_feedback(user_id) is None else False
