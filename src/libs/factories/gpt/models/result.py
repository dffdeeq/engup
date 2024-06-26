import typing as T  # noqa
from pydantic import BaseModel

from src.libs.factories.gpt.models.competence_result import CompetenceResults, SimpleCompetenceResults


class Result(BaseModel):
    overall_score: float
    competence_results: CompetenceResults
    vocabulary: T.List[str]


class SimpleResult(BaseModel):
    overall_score: float
    competence_results: SimpleCompetenceResults
