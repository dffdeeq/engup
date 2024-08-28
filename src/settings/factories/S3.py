import typing as T # noqa

from pydantic import Field

from src.settings.factory import SettingsFactory


class S3Settings(SettingsFactory):
    aws_access_key: str = Field(description='AWS access key')
    aws_secret_key: str = Field(description='AWS secret key')
    endpoint_url: str = Field(description='s3 endpoint url')

    @classmethod
    def from_dict(cls, settings_dict: T.Dict[str, str]) -> 'S3Settings':
        return S3Settings(
            aws_access_key=settings_dict.get('S3_SETTINGS_AWS_ACCESS_KEY'),
            aws_secret_key=settings_dict.get('S3_SETTINGS_AWS_SECRET_KEY'),
            endpoint_url=settings_dict.get('S3_SETTINGS_ENDPOINT_URL'),
        )
