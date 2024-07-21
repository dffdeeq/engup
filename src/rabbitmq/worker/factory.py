import json
import typing as T  # noqa
import logging

from aio_pika import connect_robust, ExchangeType, Message

from src.repos.factory import RepoFactory

logger = logging.getLogger(__name__)


class RabbitMQWorkerFactory:
    def __init__(
        self,
        repo: RepoFactory,
        dsn_string: str,
        queue_name: str,
        exchange_name: str = 'direct',
    ):
        self.repo = repo
        self.dsn_string = dsn_string
        self.exchange_name = exchange_name
        self.queue_name = queue_name

        self.exchange = None

    async def start_listening(self, routing_key: str, func: T.Callable):
        logger.info('Starting listening')
        connection = await connect_robust(self.dsn_string)
        channel = await connection.channel()
        self.exchange = await channel.declare_exchange(self.exchange_name, ExchangeType.DIRECT)
        queue = await channel.declare_queue(self.queue_name)
        await queue.bind(self.exchange, routing_key=routing_key)

        logger.info('Ready for incoming messages')
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():  # noqa
                    payload = json.loads(message.body)  # noqa
                    payload['priority'] = message.priority  # noqa
                    logger.info(f'Received {str(payload)[:50]}')
                    await func(payload)

    async def publish(
        self,
        json_serializable_dict: T.Dict,
        routing_key: str,
        priority: int = 0
    ):
        message = Message(
            body=bytes(json.dumps(json_serializable_dict), 'utf-8'),
            content_type='json',
        )
        message.priority = priority
        await self.exchange.publish(message, routing_key=routing_key)
        logger.info(f"Message published to {routing_key} with priority {priority}")

    @staticmethod
    def get_priority(priority: bool) -> int:
        return 5 if priority else 0
