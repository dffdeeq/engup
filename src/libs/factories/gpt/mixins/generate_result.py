import typing as T # noqa

from src.libs.factories.gpt.base import BaseGPTClient
from src.libs.factories.gpt.models.answer_generate import AnswerGenerate
from src.libs.factories.gpt.models.competence import Competence
from src.libs.factories.gpt.models.result import Result
from src.libs.factories.gpt.routes import GENERATE_ANSWERS


class GenerateResultMixin(BaseGPTClient):
    async def generate_result(self, competence: Competence, text: str) -> Result:
        questions_generate = AnswerGenerate(competence=competence)
        response = await self.request(
            'POST',
            GENERATE_ANSWERS,
            data={'text': text},
            params=questions_generate.dict(),
        )
        print(response.body)
        return Result(**response.body.get('response'))
