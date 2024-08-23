import os.path
import typing as T  # noqa

import boto3
from boto3 import Session
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.libs.adapter import Adapter
from src.repos.factories.temp_data import TempDataRepo
from src.services.factory import ServiceFactory
from src.settings import Settings
from src.settings.static import TEMP_FILES_DIR


class S3Service(ServiceFactory):
    def __init__(
        self,
        repo: TempDataRepo,
        adapter: Adapter,
        session: async_sessionmaker,
        settings: Settings
    ) -> None:
        super().__init__(repo, adapter, session, settings)
        self.session: Session = boto3.session.Session()
        self.s3 = self.session.client(
            service_name='s3',
            aws_access_key_id=self.settings.s3.aws_access_key,
            aws_secret_access_key=self.settings.s3.aws_secret_key,
            endpoint_url=self.settings.s3.endpoint_url
        )

    def upload_file(
        self,
        upload_filepath: str,
        object_name: str = None,
        object_dir: str = '',
        bucket_name: str = 'ielts-user-recorded-voice-files',
    ):
        object_name = object_name if object_name else os.path.basename(upload_filepath)
        self.s3.upload_file(upload_filepath, bucket_name, object_dir + object_name)

    def download_file(
        self,
        object_name: str,
        download_dir: str = TEMP_FILES_DIR,
        bucket_name: str = 'ielts-user-recorded-voice-files'
    ):
        self.s3.download_file(bucket_name, object_name, os.path.join(download_dir, object_name))

    def download_files_list(self, file_keys: T.List, bucket_name: str = 'ielts-user-recorded-voice-files'):
        for file_key in file_keys:
            self.download_file(file_key, bucket_name=bucket_name)
