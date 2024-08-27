import typing as T  # noqa
from pydantic import BaseModel

from src.libs.factories.gpt.models.suggestion import Suggestion, SimpleSuggestion


class CompetenceResults(BaseModel):
    task_achievement: T.Optional[Suggestion] = None
    fluency_coherence: Suggestion
    lexical_resources: Suggestion
    grammatical_range: Suggestion


class SimpleCompetenceResults(BaseModel):
    task_achievement: SimpleSuggestion
    coherence_cohesion: SimpleSuggestion
    lexical_resources: SimpleSuggestion
    grammatical_range: SimpleSuggestion
