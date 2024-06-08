import typing as T # noqa

from src.libs.factories.apihost.base import BaseApiHostClient
from src.libs.factories.apihost.mixins.send_audio import SpeechToTextMixin
from src.libs.http_client import HttpClient
from src.settings.factories.apihost import ApiHostSettings


class ApiHostClient(
    SpeechToTextMixin,
    BaseApiHostClient
):
    def __init__(self, http_client: HttpClient, settings: ApiHostSettings):
        super().__init__(http_client, settings)
