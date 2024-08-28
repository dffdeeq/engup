from sqlalchemy import Column, DateTime, BigInteger, String, func, Integer, ForeignKey, JSON
from sqlalchemy.orm import relationship, backref

from src.postgres.base import Base


class TgUser(Base):
    __tablename__ = 'tg_user'

    id = Column(BigInteger, primary_key=True, nullable=False)
    username = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), default=func.now())

    pts = Column(Integer, server_default='3')

    completed_questions = Column(Integer, server_default='0')
    referrer_id = Column(BigInteger, ForeignKey('tg_user.id'), nullable=True)
    referrer = relationship('TgUser', remote_side='TgUser.id', backref=backref('referrals', lazy='dynamic'))

    utm_data_json = Column(JSON, nullable=True)
