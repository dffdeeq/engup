import typing as T # noqa

from pydantic import Field

from src.settings.factory import SettingsFactory


class BotSettings(SettingsFactory):
    bot_token: str = Field(description="Telegram bot token")
    admin_ids: list[str] = Field(description="List of admins IDs")
    support_group_id: int = Field(description="Support group ID")
    mini_app_pronunciation_url: str = Field(description="Mini app pronunciation url")

    @classmethod
    def from_dict(cls, settings_dict: T.Dict[str, str]) -> 'BotSettings':
        return BotSettings(
            bot_token=settings_dict.get('BOT_SETTINGS_BOT_TOKEN'),
            admin_ids=settings_dict.get('BOT_SETTINGS_ADMIN_IDS').split(','),
            support_group_id=settings_dict.get('BOT_SETTINGS_SUPPORT_GROUP_ID'),
            mini_app_pronunciation_url=settings_dict.get('BOT_SETTINGS_MINI_APP_PRONUNCIATION_URL'),
        )
