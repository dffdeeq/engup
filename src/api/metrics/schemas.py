import uuid
from pydantic import BaseModel


class MetricsData(BaseModel):
    uuid: uuid.UUID
    metrics_string: str
