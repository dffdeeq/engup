from sqlalchemy import Integer, Column, ForeignKey, func, BigInteger, DateTime, String

from src.postgres.base import Base


class TgUserWallet(Base):
    __tablename__ = 'tg_user_wallet'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('tg_user.id', ondelete='CASCADE'))

    channel = Column(String)

    amount = Column(Integer)
    currency = Column(String)

    timestamp = Column(DateTime, default=func.now())
