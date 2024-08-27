import os
import typing as T  # noqa
import uuid

from aiogram import Bot
from aiogram.types import Voice
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.libs.adapter import Adapter
from src.repos.factories.question import QuestionRepo
from src.services.factories.S3 import S3Service
from src.services.factory import ServiceFactory
from src.settings import Settings
from src.settings.static import TEMP_FILES_DIR


class VoiceService(ServiceFactory):
    def __init__(
        self,
        s3_service: S3Service,
        repo: QuestionRepo,
        adapter: Adapter,
        session: async_sessionmaker,
        settings: Settings
    ) -> None:
        super().__init__(repo, adapter, session, settings)
        self.repo = repo
        self.s3_service = s3_service

    async def save_user_voicemail(self, voice: Voice, bot_instance: Bot) -> str:
        file = await self._convert_telegram_voice_to_binary(voice, bot_instance)
        filename = uuid.uuid4().hex + '.ogg'
        filepath = os.path.join(TEMP_FILES_DIR, filename)
        self.s3_service.upload_file_obj(file, filename=filename)
        return filepath

    @staticmethod
    async def _convert_telegram_voice_to_binary(voice: Voice, bot_instance: Bot) -> T.Optional[T.BinaryIO]:
        file_info = await bot_instance.get_file(voice.file_id)
        file = await bot_instance.download_file(file_info.file_path)
        return file
