from aiogram.filters import Filter

from src.bot.injector.base import BaseInjector


class _SubscriptionServiceInjector(Filter):
    def __init__(self, subscription_service):
        self.subscription_service = subscription_service

    async def __call__(self, *args, **kwargs):
        return {'subscription_service': self.subscription_service}


class SubscriptionServiceInjectorMixin(BaseInjector):
    @property
    def inject_subscription(self) -> _SubscriptionServiceInjector:
        return _SubscriptionServiceInjector(self.subscription_service)
