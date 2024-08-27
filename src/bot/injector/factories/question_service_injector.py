from aiogram.filters import Filter

from src.bot.injector.base import BaseInjector


class _QuestionServiceInjector(Filter):
    def __init__(self, question_service):
        self.question_service = question_service

    async def __call__(self, *args, **kwargs):
        return {'question_service': self.question_service}


class QuestionServiceInjectorMixin(BaseInjector):
    @property
    def inject_question(self) -> _QuestionServiceInjector:
        return _QuestionServiceInjector(self.question_service)
