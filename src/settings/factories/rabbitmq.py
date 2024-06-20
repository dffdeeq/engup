import typing as T # noqa

from pydantic import Field

from src.settings.factory import SettingsFactory


class RabbitMQSettings(SettingsFactory):
    # **** Core ****
    host: str = Field(default='localhost', description='RABBITMQ_SETTINGS_HOST')
    port: int = Field(default='5672', description='RABBITMQ_SETTINGS_PORT')
    user: str = Field(default='root', description='RabbitMQ user')
    password: str = Field(default='root', description='RabbitMQ password')

    @classmethod
    def from_dict(cls, settings_dict: T.Dict[str, str]) -> 'RabbitMQSettings':
        return RabbitMQSettings(
            host=settings_dict.get('RABBITMQ_SETTINGS_HOST'),
            port=settings_dict.get('RABBITMQ_SETTINGS_PORT'),
            user=settings_dict.get('RABBITMQ_SETTINGS_USER'),
            password=settings_dict.get('RABBITMQ_SETTINGS_PASSWORD'),
        )

    @property
    def dsn(self) -> str:
        """
        RabbitMQ dsn string.

        :return: RabbitMQ dsn string.
        """
        return f'amqp://{self.user}:{self.password}@{self.host}:{self.port}'
