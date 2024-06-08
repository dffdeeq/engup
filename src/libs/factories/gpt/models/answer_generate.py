from pydantic import BaseModel

from src.libs.factories.gpt.models.competence import Competence


class AnswerGenerate(BaseModel):
    competence: Competence
    text: str

    def dict(self, *args, **kwargs):
        d = super().dict(*args, **kwargs)
        d['competence'] = d['competence'].value
        return d
