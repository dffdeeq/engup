import typing as T  # noqa

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.postgres.enums import PartEnum
from src.postgres.models.temp_data import TempData
from src.repos.factory import RepoFactory


class TempDataRepo(RepoFactory):
    def __init__(self, model: T.Type[TempData], session: async_sessionmaker):
        super().__init__(model, session)

    async def insert_temp_data(
        self,
        tg_user_question_id: int,
        part: PartEnum,
        question_text: str,
        filename: str
    ) -> TempData:
        instance = await self.insert_many({
            'tg_user_question_id': tg_user_question_id,
            'part': part.value,
            'question_text': question_text,
            'filename': filename,
        })
        return instance[0]

    async def get_temp_data(self, conditions: T.Dict) -> T.Optional[TempData]:
        async with self.session() as session:
            query = select(self.model).where(
                *[getattr(self.model, k) == v for k, v in conditions.items()]
            )
            result = await session.execute(query)
            return result.scalar_one_or_none()
