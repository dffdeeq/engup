from aiogram.filters import Filter

from src.bot.injector.base import BaseInjector


class _ApiHostClientInjector(Filter):
    def __init__(self, apihost_client):
        self.apihost_client = apihost_client

    async def __call__(self, *args, **kwargs):
        return {'apihost_client': self.apihost_client}


class ApiHostClientInjectorMixin(BaseInjector):
    @property
    def inject_apihost(self) -> _ApiHostClientInjector:
        return _ApiHostClientInjector(self.apihost_client)
