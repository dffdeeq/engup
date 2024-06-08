from pydantic import BaseModel


class Question(BaseModel):
    card_title: str
    card_body: str
