import os
import typing as T  # noqa
import uuid

from aiogram import Bot
from aiogram.types import Voice
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.libs.adapter import Adapter
from src.postgres.models.temp_data import TempData
from src.repos.factories.question import QuestionRepo
from src.services.factory import ServiceFactory
from src.settings import Settings
from src.settings.static import TEMP_FILES_DIR


class VoiceService(ServiceFactory):
    def __init__(self, repo: QuestionRepo, adapter: Adapter, session: async_sessionmaker, settings: Settings) -> None:
        super().__init__(repo, adapter, session, settings)
        self.repo = repo

    async def save_user_voicemail(self, voice: Voice, bot_instance: Bot) -> str:
        file = await self._convert_telegram_voice_to_file(voice, bot_instance)
        filename = os.path.join(TEMP_FILES_DIR, uuid.uuid4().hex)
        self._download_file(file, filename)
        return filename

    @staticmethod
    async def _convert_telegram_voice_to_file(voice: Voice, bot_instance: Bot):
        file_info = await bot_instance.get_file(voice.file_id)
        file = await bot_instance.download_file(file_info.file_path)
        return file

    @staticmethod
    def _download_file(file: T.BinaryIO, filename: str):
        with open(filename, 'wb') as f:
            f.write(file.read())

    async def insert_into_temp_data(
        self,
        tg_user_question_id: int,
        first_file_name: str,
        first_part_questions: T.List[str],
        second_part_question: str,
        third_part_questions: T.List[str],
    ) -> TempData:
        instance = await self.repo.insert_one(
            model=TempData,
            tg_user_question_id=tg_user_question_id,
            first_file_name=first_file_name,
            first_part_questions=first_part_questions,
            second_part_question=second_part_question,
            third_part_questions=third_part_questions
        )
        return instance
