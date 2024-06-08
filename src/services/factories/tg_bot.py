import typing as T  # noqa

from sqlalchemy.ext.asyncio import AsyncSession

from src.libs.adapter import Adapter
from src.postgres.models.tg_user import TgUser
from src.repos.factories.user import TgUserRepo
from src.services.factory import ServiceFactory
from src.settings import Settings


class TgBotService(ServiceFactory):
    def __init__(self, repo: TgUserRepo, adapter: Adapter, session: AsyncSession, settings: Settings) -> None:
        super().__init__(repo, adapter, session, settings)
        self.repo = repo

    async def get_or_create_tg_user(self, tg_id: int, username: T.Optional[str] = None) -> TgUser:
        user = await self.repo.get_tg_user_by_tg_id(tg_id=tg_id)
        if not user:
            user = await self.repo.create_tg_user(tg_id=tg_id, username=username)
        return user
