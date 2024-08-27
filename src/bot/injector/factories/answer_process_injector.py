from aiogram.filters import Filter

from src.bot.injector.base import BaseInjector


class _AnswerProcessInjector(Filter):
    def __init__(self, answer_process):
        self.answer_process = answer_process

    async def __call__(self, *args, **kwargs):
        return {'answer_process': self.answer_process}


class AnswerProcessInjectorMixin(BaseInjector):
    @property
    def inject_answer_process(self) -> _AnswerProcessInjector:
        return _AnswerProcessInjector(self.answer_process)
