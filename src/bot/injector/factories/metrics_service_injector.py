from aiogram.filters import Filter

from src.bot.injector.base import BaseInjector


class _MetricsServiceInjector(Filter):
    def __init__(self, metrics_service):
        self.metrics_service = metrics_service

    async def __call__(self, *args, **kwargs):
        return {'metrics_service': self.metrics_service}


class MetricsServiceInjectorMixin(BaseInjector):
    @property
    def inject_metrics_service(self) -> _MetricsServiceInjector:
        return _MetricsServiceInjector(self.metrics_service)
