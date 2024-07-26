from sqlalchemy import Integer, Column, ForeignKey, func, BigInteger, DateTime, String

from src.postgres.base import Base


class TgUserPts(Base):
    __tablename__ = 'tg_user_pts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('tg_user.id'))

    pts_channel = Column(String)
    balance_movement = Column(Integer)

    timestamp = Column(DateTime, default=func.now())
