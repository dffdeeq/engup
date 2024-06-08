import typing as T # noqa
from pydantic import BaseModel, Field


class STTText(BaseModel):
    text: str
