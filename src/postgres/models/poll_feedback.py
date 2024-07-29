from sqlalchemy import Integer, Column, JSON, ForeignKey, BigInteger, DateTime, func

from src.postgres.base import Base


class PollFeedback(Base):
    __tablename__ = 'poll_feedback'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('tg_user.id'))
    feedback_json = Column(JSON)

    created_at = Column(DateTime(timezone=True), default=func.now())
