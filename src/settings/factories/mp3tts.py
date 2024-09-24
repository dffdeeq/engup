import typing as T # noqa

from pydantic import Field

from src.settings.factory import SettingsFactory


class MP3TTSSettings(SettingsFactory):
    url: str = Field(description='URL of the Apihost server')
    auth_token: str = Field(description="Apihost Authorization token")
    webhook_url: str = Field(description='Webhook URL')
    debug_mode: bool = Field(description='Debug mode')

    @classmethod
    def from_dict(cls, settings_dict: T.Dict[str, str]) -> 'MP3TTSSettings':
        return MP3TTSSettings(
            url=settings_dict.get('MP3TTS_SETTINGS_URL'),
            auth_token=settings_dict.get('MP3TTS_SETTINGS_AUTH_TOKEN'),
            webhook_url=settings_dict.get('MP3TTS_SETTINGS_WEBHOOK_URL'),
            debug_mode=settings_dict.get('MP3TTS_SETTINGS_DEBUG_MODE')
        )
