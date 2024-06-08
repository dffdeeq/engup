import typing as T # noqa
from abc import ABC, abstractmethod

from pydantic import BaseModel


class SettingsFactory(ABC, BaseModel):
    @classmethod
    @abstractmethod
    def from_dict(cls, settings_dict: T.Dict[str, str]):
        raise NotImplemented
