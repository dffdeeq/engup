from aiogram.filters import Filter

from src.bot.injector.base import BaseInjector


class _FeedbackServiceInjector(Filter):
    def __init__(self, feedback_service):
        self.feedback_service = feedback_service

    async def __call__(self, *args, **kwargs):
        return {'feedback_service': self.feedback_service}


class FeedbackInjectorMixin(BaseInjector):
    @property
    def inject_feedback_service(self) -> _FeedbackServiceInjector:
        return _FeedbackServiceInjector(self.feedback_service)
