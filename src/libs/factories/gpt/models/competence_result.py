import typing as T  # noqa
from pydantic import BaseModel

from src.libs.factories.gpt.models.suggestion import Suggestion


class CompetenceResults(BaseModel):
    task_achievement: T.Optional[Suggestion] = None
    fluency_coherence: Suggestion
    lexical_resources: Suggestion
    grammatical_range: Suggestion
