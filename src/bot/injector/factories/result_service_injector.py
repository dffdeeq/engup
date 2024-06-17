from aiogram.filters import Filter

from src.bot.injector.base import BaseInjector


class _ResultServiceInjector(Filter):
    def __init__(self, result_service):
        self.result_service = result_service

    async def __call__(self, *args, **kwargs):
        return {'result_service': self.result_service}


class ResultServiceInjectorMixin(BaseInjector):
    @property
    def inject_result(self) -> _ResultServiceInjector:
        return _ResultServiceInjector(self.result_service)
