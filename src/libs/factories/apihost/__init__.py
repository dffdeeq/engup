import typing as T  # noqa

from src.libs.factories.apihost.mixins.get_synthesize import GetSynthesizeMixin
from src.libs.factories.apihost.mixins.send_to_synthesize import SendTextToSynthesizeMixin
from src.libs.http_client import HttpClient
from src.settings.factories.apihost import ApiHostSettings


class ApihostClient(
    SendTextToSynthesizeMixin,
    GetSynthesizeMixin
):
    def __init__(self, http_client: HttpClient, settings: ApiHostSettings):
        super().__init__(http_client, settings)
