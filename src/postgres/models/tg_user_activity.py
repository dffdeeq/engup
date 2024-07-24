from sqlalchemy import ForeignKey, Column, Integer, DateTime, BigInteger, func

from src.postgres.base import Base


class TgUserActivity(Base):
    __tablename__ = 'tg_user_activity'

    id = Column(Integer, primary_key=True, autoincrement=True)

    user_id = Column(BigInteger, ForeignKey('tg_user.id'), nullable=False)
    activity_id = Column(ForeignKey('activity.id'), nullable=False)

    activity_timestamp = Column(DateTime(timezone=True), default=func.now())
