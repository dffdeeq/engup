from aiogram.filters import Filter

from src.bot.injector.base import BaseInjector


class _GPTProducerInjector(Filter):
    def __init__(self, gpt_producer):
        self.gpt_producer = gpt_producer

    async def __call__(self, *args, **kwargs):
        return {'gpt_producer': self.gpt_producer}


class GPTProducerInjectorMixin(BaseInjector):
    @property
    def inject_gpt_producer(self) -> _GPTProducerInjector:
        return _GPTProducerInjector(self.gpt_producer)
