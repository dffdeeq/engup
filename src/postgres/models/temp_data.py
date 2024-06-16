from sqlalchemy import Column, BigInteger, String, ForeignKey, ARRAY, JSON, UUID

from src.postgres.base import Base


class TempData(Base):
    __tablename__ = 'temp_data'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    tg_user_question_id = Column(ForeignKey('tg_user_question.id'), nullable=False)
    first_file_name = Column(String, nullable=False)

    first_part_questions = Column(ARRAY(String), nullable=False)
    second_part_question = Column(String, nullable=False)
    third_part_questions = Column(ARRAY(String), nullable=False)
