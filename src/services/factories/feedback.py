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

    async def save_user_poll_feedback(
        self,
        user_id: int,
        feedback_dict: T.Dict,
        poll_type: str = 'new_user'
    ) -> PollFeedback:
        return await self.repo.create_user_poll_feedback(user_id, feedback_dict, poll_type)

    async def user_can_get_free_points(self, user_id: int, survey_type: str) -> bool:
        return True if await self.repo.get_user_poll_feedback(user_id, survey_type) is None else False

    async def save_user_review(self, user_id: int, rating: int, text: str):
        return await self.repo.create_user_review(user_id, rating, text)
