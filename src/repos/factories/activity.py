import typing as T  # noqa

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.postgres.models.activity import Activity
from src.postgres.models.tg_user_activity import TgUserActivity
from src.repos.factory import RepoFactory


class ActivityRepo(RepoFactory):
    def __init__(self, model: T.Type[TgUserActivity], session: async_sessionmaker):
        super().__init__(model, session)

    async def get_activity(self, activity_name: str) -> T.Optional[Activity]:
        async with self.session() as session:
            query = select(Activity).where(and_(Activity.name == activity_name))
            result = await session.execute(query)
            instance = result.scalar_one_or_none()
            return instance

    async def create_user_activity(self, user_id: int, activity_id: int) -> TgUserActivity:
        instance = await self.insert_one(user_id=user_id, activity_id=activity_id)
        return instance
