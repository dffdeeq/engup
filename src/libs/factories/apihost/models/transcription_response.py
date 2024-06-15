import uuid

from pydantic import BaseModel


class TranscriptionResponse(BaseModel):
    transcribe_id: uuid.UUID
