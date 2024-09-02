from sqlalchemy import Integer, Column, Enum, JSON, Boolean, DateTime, func, String

from src.postgres.base import Base
from src.postgres.enums import CompetenceEnum


class Question(Base):
    __tablename__ = 'question'

    id = Column(Integer, primary_key=True, autoincrement=True)
    competence = Column(Enum(CompetenceEnum))
    question_json = Column(JSON)
    is_active = Column(Boolean, default=True)
    date_modified = Column(DateTime, default=func.now(), onupdate=func.now())

    question_audio_json = Column(JSON, nullable=True)


class QuestionAudioFile(Base):
    __tablename__ = 'question_audio_file'

    id = Column(Integer, primary_key=True, autoincrement=True)

    text_hash = Column(String, nullable=True)
    filename = Column(String, nullable=True)
