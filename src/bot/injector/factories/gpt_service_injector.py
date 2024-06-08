from aiogram.filters import Filter

from src.bot.injector.base import BaseInjector


class _GPTServiceInjector(Filter):
    def __init__(self, gpt_service):
        self.gpt_service = gpt_service

    async def __call__(self, *args, **kwargs):
        return {'gpt_service': self.gpt_service}


class GPTServiceInjectorMixin(BaseInjector):
    @property
    def inject_gpt(self) -> _GPTServiceInjector:
        return _GPTServiceInjector(self.gpt_service)
