from pydantic import BaseModel

from src.libs.factories.gpt.models.competence import Competence


class QuestionsGenerate(BaseModel):
    competence: Competence
    question_number: int

    def dict(self, *args, **kwargs):
        d = super().dict(*args, **kwargs)
        d['competence'] = d['competence'].value
        return d
