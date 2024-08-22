import typing as T # noqa

from src.libs.factories.analytics.base import BaseAnalyticsClient
from src.libs.factories.analytics.mixins.send_event import SendEventMixin
from src.libs.http_client import HttpClient
from src.settings import AnalyticsSettings


class AnalyticsClient(
    SendEventMixin,
    BaseAnalyticsClient
):
    def __init__(self, http_client: HttpClient, settings: AnalyticsSettings) -> None:
        super().__init__(http_client, settings)
