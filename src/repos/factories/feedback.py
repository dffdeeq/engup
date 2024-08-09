import typing as T  # noqa

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.postgres.models.poll_feedback import PollFeedback, TgUserReview
from src.repos.factory import RepoFactory


class FeedbackRepo(RepoFactory):
    def __init__(self, model: T.Type[PollFeedback], session: async_sessionmaker):
        super().__init__(model, session)

    async def create_user_poll_feedback(self, user_id: int, feedback_dict: T.Dict) -> PollFeedback:
        return await self.insert_one(user_id=user_id, feedback_json=feedback_dict)

    async def get_user_poll_feedback(self, user_id: int) -> T.Optional[PollFeedback]:
        async with self.session() as session:
            query = select(self.model).where(self.model.user_id == user_id)
            result = await session.execute(query)
            return result.scalars().first()

    async def create_user_review(self, user_id: int, rating: int, text: str):
        return await self.insert_one(model=TgUserReview, user_id=user_id, rating=rating, text=text)
