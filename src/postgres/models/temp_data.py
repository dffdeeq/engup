from sqlalchemy import Column, BigInteger, String, ForeignKey, Enum

from src.postgres.base import Base
from src.postgres.enums import PartEnum


class TempData(Base):
    __tablename__ = 'temp_data'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    tg_user_question_id = Column(ForeignKey('tg_user_question.id'), nullable=False)

    part = Column(Enum(PartEnum))
    question_text = Column(String, nullable=True)
    filename = Column(String, nullable=True)
    answer_text = Column(String, nullable=True)
