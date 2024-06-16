import typing as T  # noqa
from pydantic import BaseModel


class Transcription(BaseModel):
    name: str
    text: str
    status: T.Optional[str]


class TranscriptionData(BaseModel):
    transcriptions: T.List[Transcription]
