from sqlalchemy import Integer, Column, ForeignKey, func, BigInteger, DateTime, String

from src.postgres.base import Base


class Currency(Base):
    __tablename__ = 'currency'

    id = Column(Integer, primary_key=True)
    code = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)


class TgUserWallet(Base):
    __tablename__ = 'tg_user_wallet'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('tg_user.id'))

    channel = Column(String)

    amount = Column(Integer)
    currency_id = Column(Integer, ForeignKey('currency.id'))

    timestamp = Column(DateTime, default=func.now())
