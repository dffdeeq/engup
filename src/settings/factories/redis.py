import typing as T # noqa

from pydantic import Field

from src.settings.factory import SettingsFactory


class RedisSettings(SettingsFactory):
    # **** Core ****
    host: str = Field(default='localhost', description='REDIS_SETTINGS_HOST')
    port: int = Field(default=6379, description='REDIS_SETTINGS_PORT')

    @classmethod
    def from_dict(cls, settings_dict: T.Dict[str, str]) -> 'RedisSettings':
        return RedisSettings(
            host=settings_dict.get('REDIS_SETTINGS_HOST'),
            port=settings_dict.get('REDIS_SETTINGS_PORT'),
        )

    @property
    def dsn(self) -> str:
        """
        Redis dsn string.

        :return: Redis dsn string.
        """
        return f'redis://{self.host}:{self.port}'
