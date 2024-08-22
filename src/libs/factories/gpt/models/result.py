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


class TranscriptResult(BaseModel):
    text: str
    self_correction_list: T.List[str]
    repetitions_list: T.List[str]
