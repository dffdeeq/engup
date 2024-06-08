import typing as T # noqa

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.postgres.models.tg_user import TgUser
from src.repos.factory import RepoFactory


class TgUserRepo(RepoFactory):
    def __init__(self, model: T.Type[TgUser], session: AsyncSession):
        super().__init__(model, session) # noqa

    async def get_tg_user_by_tg_id(self, tg_id: int) -> T.Optional[TgUser]:
        async with self.session() as session:
            stmt = select(TgUser).filter(TgUser.tg_id == tg_id)  # noqa
            user = await session.execute(stmt)
            return user.scalar_one_or_none()

    async def create_tg_user(self, tg_id: int, username: T.Optional[str]) -> TgUser:
        user_obj = await self.insert_one(tg_id=tg_id, username=username)
        return user_obj
