import typing as T  # noqa

from sqlalchemy.ext.asyncio import async_sessionmaker

from src.libs.adapter import Adapter
from src.repos.factories.temp_data import TempDataRepo
from src.services.factory import ServiceFactory
from src.settings import Settings


class AnswerProcessService(ServiceFactory):
    def __init__(self, repo: TempDataRepo, adapter: Adapter, session: async_sessionmaker, settings: Settings) -> None:
        super().__init__(repo, adapter, session, settings)
        self.repo = repo

    async def insert_into_temp_data(
        self,
        tg_user_question_id: int,
        first_file_name: str,
        first_part_questions: T.List[str],
        second_part_question: str,
        third_part_questions: T.List[str],
    ):
        instance = await self.repo.insert(
            tg_user_question_id=tg_user_question_id,
            first_file_name=first_file_name,
            first_part_questions=first_part_questions,
            second_part_question=second_part_question,
            third_part_questions=third_part_questions
        )
        return instance
