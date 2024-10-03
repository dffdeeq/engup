import pydantic


class TgUserQuestionSchema(pydantic.BaseModel):
    question_id: int
    user_id: int
    status: bool
