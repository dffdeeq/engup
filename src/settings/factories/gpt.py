import typing as T # noqa

from pydantic import Field

from src.settings.factory import SettingsFactory


class GPTSettings(SettingsFactory):
    url: str = Field(description='URL of the GPT server')
    auth_token: str = Field(description="Authorization token")

    @classmethod
    def from_dict(cls, settings_dict: T.Dict[str, str]) -> 'GPTSettings':
        return GPTSettings(
            url=settings_dict.get('GPT_SETTINGS_URL'),
            auth_token=settings_dict.get('GPT_SETTINGS_AUTH_TOKEN'),
        )
