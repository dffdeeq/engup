import typing as T  # noqa
from pathlib import Path

from aio_pika.abc import AbstractRobustConnection
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.rabbitmq.consumer.factory import RabbitMQWorkerFactory
from src.services.factories.apihost import ApiHostService


class ApiHostWorker(RabbitMQWorkerFactory):
    def __init__(
        self,
        connection_pool: AbstractRobustConnection,
        queue_name: str,
        routing_key: str,
        session: async_sessionmaker,
        apihost_service: ApiHostService,
    ):
        super().__init__(connection_pool, queue_name, routing_key)
        self.session = session
        self.apihost_service = apihost_service

    async def send_files_to_transcription_and_clear(self, filepaths: dict) -> None:
        await self.apihost_service.send_to_transcription(filepaths['files'])
        self.clear_temp_files(filepaths['files'])

    @staticmethod
    def clear_temp_files(filepaths: T.List[str]) -> None:
        for file in filepaths:
            path = Path(file)
            if path.exists():
                path.unlink()
