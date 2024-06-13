from aio_pika.abc import AbstractRobustConnection
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.postgres.enums import CompetenceEnum
from src.rabbitmq.factory import WorkerFactory
from src.services.factories.gpt import GPTService


class GPTWorker(WorkerFactory):
    def __init__(
        self,
        connection_pool: AbstractRobustConnection,
        session: async_sessionmaker,
        gpt_service: GPTService,
        queue_name: str,
        routing_key: str
    ):
        super().__init__(connection_pool, session, gpt_service, queue_name, routing_key)

    async def send_text_to_get_result(self, competence: CompetenceEnum, text: str = None):
        await self.gpt_service.try_generate_result(text, competence)
