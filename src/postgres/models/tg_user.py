from sqlalchemy import Column, DateTime, BigInteger, String, func

from src.postgres.base import Base


class TgUser(Base):
    __tablename__ = 'tg_user'

    id = Column(BigInteger, primary_key=True, nullable=False)
    username = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), default=func.now())
