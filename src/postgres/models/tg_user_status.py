from sqlalchemy import Integer, Column, ForeignKey, Boolean, Date, func, BigInteger

from src.postgres.base import Base


class TgUserStatus(Base):
    __tablename__ = 'tg_user_status'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('tg_user.id'))

    flag_new_user = Column(Boolean, nullable=True)
    flag_active_user = Column(Boolean, nullable=True)
    flag_pay_user = Column(Boolean, nullable=True)
    flag_churn_user = Column(Boolean, nullable=True)
    flag_premium_user = Column(Boolean, nullable=True)
    flag_return_user = Column(Boolean, nullable=True)

    status_date = Column(Date, default=func.current_date(), nullable=False)
