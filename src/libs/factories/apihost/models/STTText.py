import typing as T # noqa
from pydantic import BaseModel


class STTText(BaseModel):
    text: str
