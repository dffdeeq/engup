from aiogram.filters import Filter

from src.bot.injector.base import BaseInjector


class _UserQuestionServiceInjector(Filter):
    def __init__(self, uq_service):
        self.uq_service = uq_service

    async def __call__(self, *args, **kwargs):
        return {'uq_service': self.uq_service}


class UserQuestionServiceInjectorMixin(BaseInjector):
    @property
    def inject_uq(self) -> _UserQuestionServiceInjector:
        return _UserQuestionServiceInjector(self.uq_service)
