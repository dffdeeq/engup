import typing as T  # noqa
from pydantic import RootModel


class Question(RootModel[T.Dict[str, T.Any]]):
    pass
