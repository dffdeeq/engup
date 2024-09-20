import typing as T  # noqa
from datetime import timedelta, datetime

from sqlalchemy.ext.asyncio import async_sessionmaker

from src.libs.adapter import Adapter
from src.postgres.models.subscription import Subscription
from src.repos.factories.subscription import SubscriptionRepo
from src.services.factory import ServiceFactory
from src.settings import Settings


class SubscriptionService(ServiceFactory):
    def __init__(
        self,
        repo: SubscriptionRepo,
        adapter: Adapter,
        session: async_sessionmaker,
        settings: Settings
    ) -> None:
        super().__init__(repo, adapter, session, settings)
        self.repo = repo

    async def get_user_active_subscription(self, user_id: int) -> Subscription:
        return await self.repo.get_user_active_subscription_or_none(user_id)

    async def get_user_subscriptions(self, user_id: int) -> T.List[Subscription]:
        return await self.repo.get_user_subscriptions(user_id)

    async def user_have_active_subscription(self, user_id: int) -> bool:
        active_sub = await self.get_user_active_subscription(user_id)
        return active_sub is not None

    async def add_subscription(self, user_id: int, sub_month: int) -> Subscription:
        subscription = await self.get_user_active_subscription(user_id)
        extended_days = sub_month * 30
        async with self.session() as session:
            if subscription:
                subscription.end_date += timedelta(days=extended_days)
                session.add(subscription)
                await session.commit()
            else:
                subscription = Subscription(
                    user_id=user_id,
                    start_date=datetime.utcnow(),
                    end_date=datetime.utcnow() + timedelta(days=extended_days),
                    status='active'
                )
                session.add(subscription)
                await session.commit()
            return subscription
