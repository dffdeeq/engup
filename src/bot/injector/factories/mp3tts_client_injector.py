from aiogram.filters import Filter

from src.bot.injector.base import BaseInjector


class _MP3TTSClientInjector(Filter):
    def __init__(self, apihost_client):
        self.apihost_client = apihost_client

    async def __call__(self, *args, **kwargs):
        return {'apihost_client': self.apihost_client}


class MP3TTSClientInjectorMixin(BaseInjector):
    @property
    def inject_mp3tts(self) -> _MP3TTSClientInjector:
        return _MP3TTSClientInjector(self.mp3tts_client)
