from aiogram.filters import Filter

from src.bot.injector.base import BaseInjector


class _S3Injector(Filter):
    def __init__(self, s3):
        self.s3 = s3

    async def __call__(self, *args, **kwargs):
        return {'s3': self.s3}


class S3InjectorMixin(BaseInjector):
    @property
    def inject_s3(self) -> _S3Injector:
        return _S3Injector(self.s3)
