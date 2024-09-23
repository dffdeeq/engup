from sqlalchemy import Column, BigInteger, ForeignKey, DateTime, func, Enum, UniqueConstraint

from src.postgres.base import Base
from src.postgres.enums import SubscriptionStatusEnum


class Subscription(Base):
    __tablename__ = 'subscription'

    id = Column(BigInteger, primary_key=True, nullable=False)
    user_id = Column(BigInteger, ForeignKey('tg_user.id', ondelete='CASCADE'), nullable=False)

    start_date = Column(DateTime(timezone=True), default=func.now())
    end_date = Column(DateTime(timezone=True), nullable=False)
    status = Column(Enum(SubscriptionStatusEnum), nullable=False)

    __table_args__ = (
        UniqueConstraint('user_id', 'status', name='unique_active_subscription'),
    )
