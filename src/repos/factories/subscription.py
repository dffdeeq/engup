import typing as T  # noqa

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.postgres.enums import SubscriptionStatusEnum
from src.postgres.models.subscription import Subscription
from src.repos.factory import RepoFactory


class SubscriptionRepo(RepoFactory):
    def __init__(self, model: T.Type[Subscription], session: async_sessionmaker):
        super().__init__(model, session)

    async def get_user_subscriptions(self, user_id: int) -> T.List[Subscription]:
        async with self.session() as session:
            query = select(self.model).where(self.model.user_id == user_id)
            result = await session.execute(query)
            return list(result.scalars().all())

    async def get_user_active_subscription_or_none(self, user_id: int) -> T.Optional[Subscription]:
        async with self.session() as session:
            query = select(self.model).where(
                and_(self.model.user_id == user_id,
                     self.model.status == SubscriptionStatusEnum.active)
            )
            result = await session.execute(query)
            return result.scalar_one_or_none()
