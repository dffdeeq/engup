import typing as T # noqa

from pydantic import Field

from src.settings.factory import SettingsFactory


class PostgresSettings(SettingsFactory):
    # ***** Core *****
    host: str = Field(default='localhost', description='PostgreSQL host')
    port: int = Field(default=5432, description='PostgreSQL port')
    name: str = Field(default='postgres', description='PostgreSQL database')
    user: str = Field(default='postgres', description='PostgreSQL user')
    password: str = Field(default='postgres', description='PostgreSQL password')

    # ***** Pool *****
    pool_size: int = Field(description='PostgreSQL pool size')
    max_overflow: int = Field(description='PostgreSQL max overflow count')

    @classmethod
    def from_dict(cls, settings_dict: T.Dict[str, str]) -> 'PostgresSettings':
        return PostgresSettings(
            host=settings_dict.get('POSTGRES_SETTINGS_HOST'),
            port=int(settings_dict.get('POSTGRES_SETTINGS_PORT', 5432)),
            name=settings_dict.get('POSTGRES_SETTINGS_NAME'),
            user=settings_dict.get('POSTGRES_SETTINGS_USER'),
            password=settings_dict.get('POSTGRES_SETTINGS_PASSWORD'),
            pool_size=int(settings_dict.get('POSTGRES_SETTINGS_POOL_SIZE', 10)),
            max_overflow=int(settings_dict.get('POSTGRES_SETTINGS_MAX_OVERFLOW', 0)),
        )

    @property
    def dsn(self) -> str:
        """
        PostgreSQL dsn string.

        :return: PostgreSQL dsn string with asycnpg driver.
        """
        return f'postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}'
