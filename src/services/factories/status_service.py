import typing as T  # noqa
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.libs.adapter import Adapter
from src.repos.factories.user_question import TgUserQuestionRepo
from src.services.factory import ServiceFactory
from src.settings import Settings


class StatusService(ServiceFactory):
    def __init__(
        self,
        user_qa_repo: TgUserQuestionRepo,
        adapter: Adapter,
        session: async_sessionmaker,
        settings: Settings
    ) -> None:
        super().__init__(user_qa_repo, adapter, session, settings)
        self.user_qa_repo = user_qa_repo

    async def change_qa_status(self, uq_id: int, status: str) -> None:
        await self.user_qa_repo.update_user_question(uq_id=uq_id, current_result_status=status)
