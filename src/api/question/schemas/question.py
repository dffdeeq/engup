import typing as T  # noqa
import pydantic

from src.api.question.schemas.test import TestSchema
from src.postgres.enums import CompetenceEnum


class QuestionObjectSchema(pydantic.BaseModel):
    competence: CompetenceEnum
    question_json: TestSchema
    is_active: T.Optional[bool] = True
    question_audio_json: T.Optional[T.Dict] = None


class QuestionObjectResponseSchema(pydantic.BaseModel):
    id: int
    competence: CompetenceEnum
    question_json: TestSchema
    is_active: T.Optional[bool] = None
    question_audio_json: T.Optional[T.Dict] = None

    class Config:
        from_attributes = True


class UpdateQuestionObjectSchema(pydantic.BaseModel):
    question_id: int
    competence: T.Optional[CompetenceEnum] = None
    question_json: T.Optional[TestSchema] = None
    is_active: T.Optional[bool] = None
    question_audio_json: T.Optional[T.Dict] = None
