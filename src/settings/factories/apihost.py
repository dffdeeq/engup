import typing as T # noqa

from pydantic import Field

from src.settings.factory import SettingsFactory


class ApiHostSettings(SettingsFactory):
    url: str = Field(description='URL of the Apihost server')
    auth_token: str = Field(description="Apihost Authorization token")
    webhook_url: str = Field(description='Webhook URL')

    @classmethod
    def from_dict(cls, settings_dict: T.Dict[str, str]) -> 'ApiHostSettings':
        return ApiHostSettings(
            url=settings_dict.get('APIHOST_SETTINGS_URL'),
            auth_token=settings_dict.get('APIHOST_SETTINGS_AUTH_TOKEN'),
            webhook_url=settings_dict.get('APIHOST_SETTINGS_WEBHOOK_URL'),
        )
