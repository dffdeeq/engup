import typing as T  # noqa

from sqlalchemy.ext.asyncio import async_sessionmaker

from src.libs.adapter import Adapter
from src.libs.factories.gpt.models.result import Result
from src.postgres.enums import CompetenceEnum
from src.repos.factories.question import QuestionRepo
from src.services.factory import ServiceFactory
from src.settings import Settings


class ResultService(ServiceFactory):
    def __init__(self, repo: QuestionRepo, adapter: Adapter, session: async_sessionmaker, settings: Settings) -> None:
        super().__init__(repo, adapter, session, settings)
        self.repo = repo

    async def generate_result(self, text: str, competence: CompetenceEnum) -> Result:
        return await self.adapter.gpt_client.generate_result(text=text, competence=competence)

    @staticmethod
    async def format_question_answer_to_text(card_text: str, user_answer: str) -> str:
        return f"Card text: {card_text}, user's text: {user_answer}"

    @staticmethod
    async def format_question_answer_to_dict(card_text: str, user_answer: str) -> T.Dict:
        return {'card_text': card_text, 'user_answer': user_answer}
