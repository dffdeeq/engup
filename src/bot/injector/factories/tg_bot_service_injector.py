from aiogram.filters import Filter

from src.bot.injector.base import BaseInjector


class _TgBotServiceInjector(Filter):
    def __init__(self, gpt_service):
        self.tg_bot_service = gpt_service

    async def __call__(self, *args, **kwargs):
        return {'tg_bot_service': self.tg_bot_service}


class TgBotServiceInjectorMixin(BaseInjector):
    @property
    def inject_tg_bot(self) -> _TgBotServiceInjector:
        return _TgBotServiceInjector(self.tg_bot_service)
