import typing as T # noqa

from src.libs.factories.gpt.base import BaseGPTClient
from src.libs.factories.gpt.models.answer import Answer
from src.libs.factories.gpt.models.answer_generate import AnswerGenerate
from src.libs.factories.gpt.models.competence import Competence
from src.libs.factories.gpt.routes import GENERATE_ANSWERS


class GenerateAnswerMixin(BaseGPTClient):
    async def generate_answer(
        self,
        competence: Competence,
        text: str
    ) -> Answer:
        questions_generate = AnswerGenerate(
            competence=competence,
            text=text
        )
        response = await self.request('POST', GENERATE_ANSWERS, params=questions_generate.dict())
        print(response.body)
        return Answer(**response.body.get('response'))
