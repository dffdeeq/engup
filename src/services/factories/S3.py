import logging
import os.path
import typing as T  # noqa
from io import BytesIO

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
        bucket_name: str = 'ielts-user-recorded-voice-files',
    ):
        object_name = object_name if object_name else os.path.basename(upload_filepath)
        self.s3.upload_file(upload_filepath, bucket_name, object_name)

    def upload_file_obj(self, file, filename: str, bucket_name: str = 'ielts-user-recorded-voice-files'):
        self.s3.upload_fileobj(file, Bucket=bucket_name, Key=filename)

    def download_file(
        self,
        object_name: str,
        download_dir: str = TEMP_FILES_DIR,
        bucket_name: str = 'ielts-user-recorded-voice-files'
    ):
        self.s3.download_file(bucket_name, object_name, os.path.join(download_dir, object_name))

    def get_file_obj(self, object_name: str, bucket_name: str = 'ielts-user-recorded-voice-files'):
        audio_stream = BytesIO()
        self.s3.download_fileobj(bucket_name, object_name, audio_stream)
        audio_stream.seek(0)
        audio_stream.name = object_name
        return audio_stream

    def download_files_list(
        self,
        file_keys: T.List,
        bucket_name: str = 'ielts-user-recorded-voice-files',
        download_dir: str = TEMP_FILES_DIR,
    ):
        for file_key in file_keys:
            try:
                self.download_file(file_key, download_dir, bucket_name)
            except Exception as e:
                logging.exception(e)
