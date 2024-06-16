import uuid

from pydantic import BaseModel


class UploadResponse(BaseModel):
    upload_id: uuid.UUID


class TranscriptionResponse(BaseModel):
    transcribe_id: uuid.UUID
