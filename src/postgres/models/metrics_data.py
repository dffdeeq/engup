from sqlalchemy import Column, UUID, String

from src.postgres.base import Base


class MetricsData(Base):
    __tablename__ = 'metrics_data'

    uuid = Column(UUID(as_uuid=True), primary_key=True)
    metrics_string = Column(String)
