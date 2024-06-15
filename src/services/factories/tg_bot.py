import os
import typing as T  # noqa
import uuid

from aiogram import Bot
from aiogram.types import Voice
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.libs.adapter import Adapter
from src.postgres.models.tg_user import TgUser
from src.repos.factories.user import TgUserRepo
from src.services.factory import ServiceFactory
from src.settings import Settings
from src.settings.static import TEMP_FILES_DIR


class TgBotService(ServiceFactory):
    def __init__(self, repo: TgUserRepo, adapter: Adapter, session: async_sessionmaker, settings: Settings) -> None:
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

    async def get_or_create_tg_user(self, user_id: int, username: T.Optional[str] = None) -> TgUser:
        user = await self.repo.get_tg_user_by_tg_id(user_id=user_id)
        if not user:
            user = await self.repo.create_tg_user(user_id=user_id, username=username)
        return user
