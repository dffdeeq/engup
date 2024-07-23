from aiogram.filters import Filter

from src.bot.injector.base import BaseInjector


class _StatusServiceInjector(Filter):
    def __init__(self, status_service):
        self.status_service = status_service

    async def __call__(self, *args, **kwargs):
        return {'status_service': self.status_service}


class StatusServiceInjectorMixin(BaseInjector):
    @property
    def inject_status(self) -> _StatusServiceInjector:
        return _StatusServiceInjector(self.status_service)
