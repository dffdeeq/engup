import typing as T  # noqa
from pydantic import BaseModel


class Enhancement(BaseModel):
    source_text: str
    enhanced_text: str
    basic_suggestion: str


class Suggestion(BaseModel):
    score: float
    enhancements: T.List[Enhancement]
