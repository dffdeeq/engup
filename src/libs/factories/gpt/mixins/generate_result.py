import logging
import time
import typing as T # noqa
from functools import wraps

from src.libs.factories.gpt.base import BaseGPTClient
from src.libs.factories.gpt.models.answer_generate import AnswerGenerate
from src.libs.factories.gpt.models.competence import Competence
from src.libs.factories.gpt.models.result import Result
from src.libs.factories.gpt.routes import GENERATE_ANSWERS


def async_timeit(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        result = await func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        logging.info(f"{func.__name__}: {elapsed_time:.4f} s.")
        return result
    return wrapper


class GenerateResultMixin(BaseGPTClient):
    @async_timeit
    async def generate_gpt_result(self, text: str, competence: Competence) -> Result:
        questions_generate = AnswerGenerate(competence=competence)
        response = await self.request(
            'POST',
            GENERATE_ANSWERS,
            data={'text': text},
            params=questions_generate.dict(),
        )
        return Result(**response.body.get('response'))
