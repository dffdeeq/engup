import typing as T  # noqa
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

    async def send_text_to_get_result_handle(self, filepaths: dict) -> None:
        await self.apihost_service.send_to_transcription(filepaths['files'])

    async def send_text_to_get_result(self, filepaths: T.List[str]) -> None:
        await self.apihost_service.send_to_transcription(filepaths)
