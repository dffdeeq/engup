import os
from dotenv import load_dotenv
from pydantic import BaseModel

from src.settings.factories.apihost import ApiHostSettings
from src.settings.factories.bot import BotSettings
from src.settings.factories.gpt import GPTSettings
from src.settings.factories.nn_models import NNModelsSettings
from src.settings.factories.postgres import PostgresSettings
from src.settings.factories.rabbitmq import RabbitMQSettings
from src.settings.factories.analytics import AnalyticsSettings
from src.settings.factories.S3 import S3Settings
from src.settings.factories.redis import RedisSettings


class Settings(BaseModel):
    bot: BotSettings
    postgres: PostgresSettings
    apihost: ApiHostSettings
    gpt: GPTSettings
    rabbitmq: RabbitMQSettings
    nn_models: NNModelsSettings
    analytics: AnalyticsSettings
    s3: S3Settings
    redis: RedisSettings

    @classmethod
    def new(cls) -> 'Settings':
        load_dotenv()
        settings_dict = dict(os.environ)

        return Settings(
            bot=BotSettings.from_dict(settings_dict),
            apihost=ApiHostSettings.from_dict(settings_dict),
            postgres=PostgresSettings.from_dict(settings_dict),
            gpt=GPTSettings.from_dict(settings_dict),
            rabbitmq=RabbitMQSettings.from_dict(settings_dict),
            nn_models=NNModelsSettings.from_dict(settings_dict),
            analytics=AnalyticsSettings.from_dict(settings_dict),
            s3=S3Settings.from_dict(settings_dict),
            redis=RedisSettings.from_dict(settings_dict),
        )
