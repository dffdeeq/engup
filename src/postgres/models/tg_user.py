from sqlalchemy import Integer, Column, DateTime, BigInteger, String, func

from src.postgres.base import Base


class TgUser(Base):
    __tablename__ = 'tg_user'

    id = Column(Integer, primary_key=True, autoincrement=True)
    tg_id = Column(BigInteger, nullable=False)
    username = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now())
