import typing as T  # noqa

import uuid
from pydantic import BaseModel


class Transcription(BaseModel):
    name: str
    text: str
    status: T.Optional[str]


class TranscriptionData(BaseModel):
    transcriptions: T.List[Transcription]

    def dump_transcriptions(self):
        return [t.model_dump() for t in self.transcriptions]


class MetricsData(BaseModel):
    uuid: uuid.UUID
    metrics_string: str
