from src.libs.factories.analytics import AnalyticsClient
from src.libs.factories.apihost import ApiHostClient
from src.libs.factories.gpt import GPTClient
from src.libs.http_client import HttpClient
from src.settings import Settings


class Adapter:
    def __init__(self, settings: Settings) -> None:
        self.http_client = HttpClient()
        self.apihost_client = ApiHostClient(self.http_client, settings.apihost)
        self.gpt_client = GPTClient(self.http_client, settings.gpt)
        self.analytics_client = AnalyticsClient(self.http_client, settings.analytics)
