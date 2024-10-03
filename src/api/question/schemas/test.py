import typing as T  # noqa
import pydantic

from src.postgres.enums import BlockTypeEnum


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
