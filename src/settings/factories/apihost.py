import typing as T # noqa

from pydantic import Field

from src.settings.factory import SettingsFactory


class ApiHostSettings(SettingsFactory):
    auth_token: str = Field(description="Auth token")

    @classmethod
    def from_dict(cls, settings_dict: T.Dict[str, str]) -> 'ApiHostSettings':
        return ApiHostSettings(
            auth_token=settings_dict.get('APIHOST_SETTING_AUTH_TOKEN'),
        )
