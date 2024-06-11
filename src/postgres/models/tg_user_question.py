from sqlalchemy import ForeignKey, Column, Integer, DateTime, Boolean, JSON, func, BigInteger

from src.postgres.base import Base


class TgUserQuestion(Base):
    __tablename__ = 'tg_user_question'

    id = Column(Integer, primary_key=True, autoincrement=True)

    user_id = Column(BigInteger, ForeignKey('tg_user.id'), primary_key=True)
    question_id = Column(ForeignKey('question.id'), primary_key=True)

    status = Column(Boolean, default=False)
    start_timestamp = Column(DateTime, default=func.now())
    send_feedback_timestamp = Column(DateTime)
    is_liked = Column(Boolean)
    user_answer_json = Column(JSON)
    user_result_json = Column(JSON)
