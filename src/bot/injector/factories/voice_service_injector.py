from aiogram.filters import Filter

from src.bot.injector.base import BaseInjector


class _VoiceServiceInjector(Filter):
    def __init__(self, voice_service):
        self.voice_service = voice_service

    async def __call__(self, *args, **kwargs):
        return {'voice_service': self.voice_service}


class VoiceServiceInjectorMixin(BaseInjector):
    @property
    def inject_voice(self) -> _VoiceServiceInjector:
        return _VoiceServiceInjector(self.voice_service)
