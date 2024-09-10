import typing as T # noqa

from src.libs.factories.mp3tts.base import BaseMP3TTSClient
from src.libs.factories.mp3tts.mixins.confirm_audio import ConfirmTranscriptionMixin
from src.libs.factories.mp3tts.mixins.send_audio import SendAudioToTranscriptionMixin
from src.libs.http_client import HttpClient
from src.settings.factories.mp3tts import MP3TTSSettings


class MP3TTSClient(
    SendAudioToTranscriptionMixin,
    ConfirmTranscriptionMixin,
    BaseMP3TTSClient
):
    def __init__(self, http_client: HttpClient, settings: MP3TTSSettings):
        super().__init__(http_client, settings)
