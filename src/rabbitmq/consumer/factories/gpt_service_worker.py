from aio_pika.abc import AbstractRobustConnection
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.postgres.enums import CompetenceEnum
from src.rabbitmq.consumer.factory import RabbitMQWorkerFactory
from src.services.factories.gpt import GPTService


class GPTWorker(RabbitMQWorkerFactory):
    def __init__(
        self,
        connection_pool: AbstractRobustConnection,
        queue_name: str,
        routing_key: str,
        session: async_sessionmaker,
        gpt_service: GPTService,
    ):
        super().__init__(connection_pool, queue_name, routing_key)
        self.session = session
        self.gpt_service = gpt_service

    async def send_text_to_get_result(self, competence: CompetenceEnum, text: str = None):
        await self.gpt_service.try_generate_result(text, competence)
