from aiogram.filters import Filter

from src.bot.injector.base import BaseInjector


class _TgUserServiceInjector(Filter):
    def __init__(self, tg_user_service):
        self.tg_user_service = tg_user_service

    async def __call__(self, *args, **kwargs):
        return {'tg_user_service': self.tg_user_service}


class TgUserServiceInjectorMixin(BaseInjector):
    @property
    def inject_tg_bot(self) -> _TgUserServiceInjector:
        return _TgUserServiceInjector(self.tg_user_service)
