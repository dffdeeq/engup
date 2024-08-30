from src.libs.factories.analytics import AnalyticsClient
from src.libs.factories.apihost import ApihostClient
from src.libs.factories.mp3tts import MP3TTSClient
from src.libs.factories.gpt import GPTClient
from src.libs.http_client import HttpClient
from src.settings import Settings


class Adapter:
    def __init__(self, settings: Settings) -> None:
        self.http_client = HttpClient()
        self.mp3tts_client = MP3TTSClient(self.http_client, settings.mp3tts)
        self.gpt_client = GPTClient(self.http_client, settings.gpt)
        self.analytics_client = AnalyticsClient(self.http_client, settings.analytics)
        self.apihost_client = ApihostClient(self.http_client, settings.apihost)
