import asyncio
import json
import logging
import typing as T  # noqa

from aio_pika import connect_robust, ExchangeType

from src.rabbitmq.worker.factory import RabbitMQWorkerFactory
from src.repos.factories.temp_data import TempDataRepo

logger = logging.getLogger(__name__)


class SimpleWorker(RabbitMQWorkerFactory):
    def __init__(
        self,
        repo: TempDataRepo,
        dsn_string: str,
        queue_name: str,
    ):
        super().__init__(repo, dsn_string, queue_name)
        self.repo = repo

        self.connection = None
        self.channel = None

    async def initialize(self):
        await self._connect()

    @staticmethod
    async def wait_for_message(queue) -> T.Optional[T.Dict]:
        try:
            async with queue.iterator() as queue_iter:
                async for message in queue_iter:
                    async with message.process():
                        payload = json.loads(message.body)
                        payload['priority'] = message.priority
                        logger.info(f'Received one message: {str(payload)[:50]}')
                        return payload
        except asyncio.CancelledError:
            logger.info("Message retrieval was cancelled.")
            return None

    async def try_get_one_message(self, routing_key: str, timeout: int = 60) -> T.Optional[T.Dict]:
        if not self.connection or self.connection.is_closed:
            await self._connect()
        queue = await self._declare_queue(routing_key)
        message_task = asyncio.create_task(self.wait_for_message(queue))
        try:
            return await asyncio.wait_for(message_task, timeout=timeout)
        except asyncio.TimeoutError:
            logger.info(f'No message received within {timeout} seconds')
            message_task.cancel()
            return None
        except Exception as e:
            logger.error(f'Error occurred: {str(e)}', exc_info=True)
            message_task.cancel()
            return None

    async def _connect(self):
        self.connection = await connect_robust(self.dsn_string + f'?heartbeat={self.heartbeat}')
        self.channel = await self.connection.channel()
        await self.channel.set_qos(prefetch_count=self.prefetch_count)
        self.exchange = await self.channel.declare_exchange(self.exchange_name, ExchangeType.DIRECT)

    async def _declare_queue(self, routing_key: str):
        queue = await self.channel.declare_queue(self.queue_name, arguments={'x-max-priority': 10})
        await queue.bind(self.exchange, routing_key=routing_key)
        return queue
