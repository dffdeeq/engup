import logging
import typing as T  # noqa

from sqlalchemy.ext.asyncio import AsyncSession

from src.libs.adapter import Adapter
from src.libs.factories.gpt.models.answer import Answer
from src.postgres.enums import CompetenceEnum
from src.postgres.models.question import Question
from src.libs.factories.gpt.models.question import Question as QuestionEnum
from src.repos.factories.question import QuestionRepo
from src.services.factory import ServiceFactory
from src.settings import Settings


class GPTService(ServiceFactory):
    def __init__(self, repo: QuestionRepo, adapter: Adapter, session: AsyncSession, settings: Settings) -> None:
        super().__init__(repo, adapter, session, settings)
        self.repo = repo

    @staticmethod
    async def questions_serializer(
        questions: T.List[QuestionEnum],
        competence: CompetenceEnum
    ) -> T.List[T.Dict[str, str]]:
        return [{
            'competence': competence,
            'question_json': question.model_dump_json(),
        } for question in questions]

    async def associate_user_and_question(
        self,
        user_id,
        question_id,
        user_answer_json: T.Optional[dict] = None,
        user_result_json: T.Optional[dict] = None,
        already_complete: bool = False
    ):
        await self.repo.associate_user_and_question(
            user_id, question_id, user_answer_json, user_result_json, already_complete)

    async def generate_and_save_questions(self, competence, question_number) -> T.List[Question]:
        questions = await self.adapter.gpt_client.generate_question(competence, question_number=question_number)
        question_objs = await self.repo.insert_many(await self.questions_serializer(questions, competence))
        return question_objs

    async def get_question_for_user(self, user_id: int, competence: CompetenceEnum) -> Question:
        question = await self.repo.get_started_question_for_user(user_id, competence)
        logging.info(question)
        if not question:
            question = await self.repo.get_new_question_for_user(user_id, competence)
            logging.info(question)
        if not question:
            new_questions = await self.generate_and_save_questions(competence, 1)
            question = new_questions[0]
            logging.info(question)

        return question

    async def get_answer(self, text: str, competence: CompetenceEnum) -> Answer:
        answer = await self.adapter.gpt_client.generate_answer(text=text, competence=competence)
        return answer
