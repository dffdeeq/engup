import typing as T  # noqa
import pydantic

from src.postgres.enums import BlockTypeEnum, CompetenceEnum


class QuestionSchema(pydantic.BaseModel):
    id: int
    content: str
    options: T.Optional[T.List[str]] = None
    answers: T.Optional[T.List[str]] = None
    correct_answer: T.List[str]


class QuestionBlockSchema(pydantic.BaseModel):
    id: int
    content: str
    block_type: BlockTypeEnum
    questions: T.List[QuestionSchema]


class QuestionSectionSchema(pydantic.BaseModel):
    id: int
    content: str
    blocks: T.List[QuestionBlockSchema]


class TestSchema(pydantic.BaseModel):
    content: str
    unique_id: int
    title: str
    sections: T.List[QuestionSectionSchema]


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


class UpdateObjectSchema(pydantic.BaseModel):
    question_id: int
    competence: T.Optional[CompetenceEnum] = None
    question_json: T.Optional[TestSchema] = None
    is_active: T.Optional[bool] = None
    question_audio_json: T.Optional[T.Dict] = None


class MessageResponse(pydantic.BaseModel):
    message: str
