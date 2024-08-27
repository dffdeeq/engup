import typing as T # noqa

from pydantic import Field

from src.settings.factory import SettingsFactory


class AnalyticsSettings(SettingsFactory):
    api_secret: str = Field(description="Api secret")
    url: str = Field(description="URL")

    @classmethod
    def from_dict(cls, settings_dict: T.Dict[str, str]) -> 'AnalyticsSettings':
        return AnalyticsSettings(
            api_secret=settings_dict.get('ANALYTICS_SETTINGS_API_SECRET'),
            url=settings_dict.get('ANALYTICS_SETTINGS_URL'),
        )
