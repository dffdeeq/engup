from sqlalchemy import Integer, Column, ForeignKey, func, BigInteger, DateTime, String

from src.postgres.base import Base


class PtsChannel(Base):
    __tablename__ = 'pts_channel'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)


class TgUserPts(Base):
    __tablename__ = 'tg_user_pts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('tg_user.id'))

    pts_channel_id = Column(Integer, ForeignKey('pts_channel.id'))
    balance_movement = Column(Integer)

    timestamp = Column(DateTime, default=func.now())
