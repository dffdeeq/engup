import typing as T # noqa

from sqlalchemy.ext.asyncio import async_sessionmaker

from src.postgres.models.temp_data import TempData
from src.repos.factory import RepoFactory


class TempDataRepo(RepoFactory):
    def __init__(self, model: T.Type[TempData], session: async_sessionmaker):
        super().__init__(model, session) # noqa

    async def insert(
        self,
        tg_user_question_id: int,
        first_file_name: str,
        first_part_questions: T.List[str],
        second_part_question: str,
        third_part_questions: T.List[str],
    ) -> TempData:
        instance = await self.insert_one(
            tg_user_question_id=tg_user_question_id,
            first_file_name=first_file_name,
            first_part_questions=first_part_questions,
            second_part_question=second_part_question,
            third_part_questions=third_part_questions
        )
        return instance
