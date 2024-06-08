import os
from dotenv import load_dotenv
from pydantic import BaseModel

from src.settings.factories.apihost import ApiHostSettings
from src.settings.factories.bot import BotSettings
from src.settings.factories.gpt import GPTSettings
from src.settings.factories.postgres import PostgresSettings


class Settings(BaseModel):
    bot: BotSettings
    postgres: PostgresSettings
    apihost: ApiHostSettings
    gpt: GPTSettings

    @classmethod
    def new(cls) -> 'Settings':
        load_dotenv()
        settings_dict = dict(os.environ)

        return Settings(
            bot=BotSettings.from_dict(settings_dict),
            apihost=ApiHostSettings.from_dict(settings_dict),
            postgres=PostgresSettings.from_dict(settings_dict),
            gpt=GPTSettings.from_dict(settings_dict),
        )
