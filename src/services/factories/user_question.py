import typing as T  # noqa

from sqlalchemy.ext.asyncio import async_sessionmaker

from src.libs.adapter import Adapter
from src.postgres.models.tg_user_question import TgUserQuestion
from src.repos.factories.user import TgUserRepo
from src.repos.factories.user_question import TgUserQuestionRepo
from src.services.factory import ServiceFactory
from src.settings import Settings


class UserQuestionService(ServiceFactory):
    def __init__(
        self,
        repo: TgUserQuestionRepo,
        adapter: Adapter,
        session: async_sessionmaker,
        settings: Settings,
        user_repo: TgUserRepo
    ):
        super().__init__(repo, adapter, session, settings)
        self.repo = repo
        self.user_repo = user_repo

    async def get_or_create_user_question(self, user_id, question_id) -> TgUserQuestion:
        instance = await self.repo.get_user_question(user_id, question_id)
        if not instance:
            instance = await self.repo.create_user_question(user_id, question_id)
        if not instance.premium_queue and await self.user_repo.deduct_point(user_id):
            async with self.session() as session:
                instance.premium_queue = True
                session.add(instance)
                await session.commit()
                await session.refresh(instance)
        return instance

    async def update_user_question(
        self,
        uq_id: int,
        answer_json: T.Optional[dict] = None,
        result_json: T.Optional[dict] = None,
        status: bool = False
    ):
        await self.repo.update_user_question(uq_id, answer_json, result_json, status)

    @staticmethod
    async def format_question_answer_to_text(card_text: str, user_answer: str) -> str:
        return f"Card text: '{card_text}', response text: '{user_answer}'"

    @staticmethod
    async def format_question_answer_to_dict(card_text: str, user_answer: str) -> T.Dict:
        return {'card_text': card_text, 'user_answer': user_answer}
