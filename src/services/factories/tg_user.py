import typing as T  # noqa
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.libs.adapter import Adapter
from src.postgres.models.tg_user import TgUser
from src.repos.factories.activity import ActivityRepo
from src.repos.factories.user import TgUserRepo
from src.services.factory import ServiceFactory
from src.settings import Settings


class TgUserService(ServiceFactory):
    def __init__(
        self,
        repo: TgUserRepo,
        activity_repo: ActivityRepo,
        adapter: Adapter,
        session: async_sessionmaker,
        settings: Settings
    ) -> None:
        super().__init__(repo, adapter, session, settings)
        self.repo = repo
        self.activity_repo = activity_repo

    async def get_or_create_tg_user(
        self,
        user_id: int,
        username: T.Optional[str] = None,
        referrer_id: int = None
    ) -> TgUser:
        user = await self.repo.get_tg_user_by_tg_id(user_id=user_id)
        if not user:
            user = await self.repo.create_tg_user(user_id=user_id, username=username, referrer_id=referrer_id)
        return user

    async def mark_user_activity(self, user_id: int, activity_name: str) -> None:
        activity = await self.activity_repo.get_activity(activity_name)
        if activity is not None:
            await self.activity_repo.create_user_activity(user_id, activity.id)
