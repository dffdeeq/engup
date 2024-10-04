import typing as T # noqa

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.postgres.models.tg_user import TgUser
from src.repos.factory import RepoFactory


class TgUserRepo(RepoFactory):
    def __init__(self, model: T.Type[TgUser], session: async_sessionmaker):
        super().__init__(model, session)

    async def deduct_point(self, user_id: int) -> T.Optional[TgUser]:
        async with self.session() as session:
            async with session.begin():
                user = await self.get_tg_user_by_tg_id(user_id, True)
                if user.pts >= 1:
                    user.pts -= 1
                    session.add(user)
                    await session.commit()
                    await session.refresh(user)
                    return user

    async def return_point(self, user_id: int) -> T.Optional[TgUser]:
        async with self.session() as session:
            async with session.begin():
                user = await self.get_tg_user_by_tg_id(user_id, True)
                user.pts += 1
                session.add(user)
                await session.commit()
                await session.refresh(user)
                return user

    async def get_tg_user_by_tg_id(self, user_id: int, for_update: bool = False) -> T.Optional[TgUser]:
        async with self.session() as session:
            query = select(TgUser).filter(and_(self.model.id == user_id))
            if for_update:
                query = query.with_for_update()
            user = await session.execute(query)
            return user.scalar_one_or_none()

    async def create_tg_user(
        self,
        user_id: int,
        username: T.Optional[str],
        referrer_id: int,
        umt_data_dict: T.Dict = None
    ) -> TgUser:
        user_obj = await self.insert_one(
            id=user_id, username=username, referrer_id=referrer_id, utm_data_json=umt_data_dict, pts=2
        )
        return user_obj
