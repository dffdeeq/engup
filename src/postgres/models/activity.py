from sqlalchemy import Integer, Column, String

from src.postgres.base import Base


class Activity(Base):
    __tablename__ = 'activity'

    id = Column(Integer, primary_key=True)
    name = Column(String)
