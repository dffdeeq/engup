import typing as T  # noqa
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.libs.adapter import Adapter
from src.postgres.enums import CompetenceEnum
from src.repos.factories.question import QuestionRepo
from src.services.factory import ServiceFactory
from src.settings import Settings
from src.libs.factories.gpt.models.question import Question as QuestionModel
from src.postgres.models.question import Question


class QuestionService(ServiceFactory):
    def __init__(self, repo: QuestionRepo, adapter: Adapter, session: async_sessionmaker, settings: Settings) -> None:
        super().__init__(repo, adapter, session, settings)
        self.repo = repo

    async def get_or_generate_question_for_user(self, user_id: int, competence: CompetenceEnum) -> Question:
        question = await self.repo.get_question_for_user(user_id, competence)
        if not question:
            new_questions = await self.generate_and_save_questions(competence, 1)
            question = new_questions[0]
        return question

    async def generate_and_save_questions(self, competence, questions_number) -> T.List[Question]:
        questions = await self.adapter.gpt_client.generate_questions(competence, question_number=questions_number)
        question_objs = await self.repo.insert_many(await self.serialize_questions(questions, competence))
        return question_objs

    @staticmethod
    async def serialize_questions(questions: T.List[QuestionModel], competence: CompetenceEnum) -> T.List[T.Dict]:
        return [{'competence': competence, 'question_json': question.model_dump_json()} for question in questions]
