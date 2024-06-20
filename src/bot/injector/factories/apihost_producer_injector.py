from aiogram.filters import Filter

from src.bot.injector.base import BaseInjector


class _ApiHostProducerInjector(Filter):
    def __init__(self, apihost_producer):
        self.apihost_producer = apihost_producer

    async def __call__(self, *args, **kwargs):
        return {'apihost_producer': self.apihost_producer}


class ApiHostProducerInjectorMixin(BaseInjector):
    @property
    def inject_apihost_producer(self) -> _ApiHostProducerInjector:
        return _ApiHostProducerInjector(self.apihost_producer)
