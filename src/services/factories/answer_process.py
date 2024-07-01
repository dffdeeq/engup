import os.path
import typing as T  # noqa

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.libs.adapter import Adapter
from src.postgres.enums import PartEnum
from src.postgres.models.temp_data import TempData
from src.repos.factories.temp_data import TempDataRepo
from src.repos.factories.user_question import TgUserQuestionRepo
from src.services.factory import ServiceFactory
from src.settings import Settings
from src.settings.static import TEMP_FILES_DIR


class AnswerProcessService(ServiceFactory):
    def __init__(
        self,
        repo: TempDataRepo,
        adapter: Adapter,
        session: async_sessionmaker,
        settings: Settings,
        user_qa_repo: TgUserQuestionRepo
    ) -> None:
        super().__init__(repo, adapter, session, settings)
        self.repo = repo
        self.user_qa_repo = user_qa_repo

    async def update_user_qa_premium_queue(self, uq_id: int, premium_queue: bool):
        await self.user_qa_repo.update(conditions={'uq_id': uq_id}, values={'premium_queue': premium_queue})

    async def insert_temp_data(self, uq_id: int, part: PartEnum, question_text: str, filename: str) -> TempData:
        """
        Update filename if temp_data already exists, otherwise insert new temp_data
        """
        if instance := await self.get_temp_data_instance_by_question_text(uq_id, question_text):
            async with self.session() as session:
                instance.filename = filename
                session.add(instance)
                await session.commit()
                await session.refresh(instance)
        else:
            instance = await self.repo.insert_temp_data(uq_id, part, question_text, filename)
        return instance

    async def get_temp_data_instance_by_question_text(self, uq_id: int, question_text: str) -> T.Optional[TempData]:
        instance = await self.repo.get_temp_data({'tg_user_question_id': uq_id, 'question_text': question_text})
        return instance

    async def get_temp_data_filepaths(self, uq_id: int) -> T.List[str]:
        instances = await self.get_many_temp_data(uq_id=uq_id)
        filenames = await self._get_filenames_from_temp_data_instances(instances)
        return [os.path.join(TEMP_FILES_DIR, f) for f in filenames]

    async def get_many_temp_data(self, uq_id: int) -> T.List[TempData]:
        async with self.session() as session:
            query = select(self.repo.model).where(self.repo.model.tg_user_question_id == uq_id)
            results = await session.execute(query)
            return list(results.scalars().all())

    @staticmethod
    async def _get_filenames_from_temp_data_instances(instances: T.List[TempData]) -> T.List[str]:
        return [instance.filename for instance in instances]
