import typing as T # noqa

from src.libs.factories.gpt.base import BaseGPTClient
from src.libs.factories.gpt.models.competence import Competence
from src.libs.factories.gpt.models.question import Question
from src.libs.factories.gpt.models.questions_generate import QuestionsGenerate
from src.libs.factories.gpt.routes import GENERATE_QUESTIONS


class GenerateQuestionsMixin(BaseGPTClient):
    async def generate_questions(
        self,
        competence: Competence,
        question_number: int
    ) -> T.List[Question]:
        questions_generate = QuestionsGenerate(
            competence=competence,
            question_number=question_number
        )
        response = await self.request('POST', GENERATE_QUESTIONS, params=questions_generate.dict())
        return [Question(**data) for data in response.body.get('response').get('tests')]
