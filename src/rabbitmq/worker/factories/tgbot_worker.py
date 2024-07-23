import json
import logging
import typing as T  # noqa
import asyncio
from functools import wraps

from aio_pika import connect_robust, ExchangeType
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.bot.core.bot import get_bot
from src.bot.injector import INJECTOR
from src.rabbitmq.worker.factory import RabbitMQWorkerFactory
from src.repos.factories.temp_data import TempDataRepo
from src.services.factories.status_service import StatusService

logger = logging.getLogger(__name__)


def async_log(func):
    @wraps(func)
    async def wrapper(self, data):
        user_id = data.get('user_id', 'Unknown user_id')
        logger.info(f"user_id: {user_id} >>> {func.__name__}")
        result = await func(self, data)
        return result
    return wrapper


class TgBotWorker(RabbitMQWorkerFactory):
    def __init__(
        self,
        session: async_sessionmaker,
        repo: TempDataRepo,
        dsn_string: str,
        queue_name: str,
        status_service: StatusService,
    ):
        super().__init__(repo, dsn_string, queue_name)
        self.repo = repo
        self.session = session
        self.bot = get_bot(INJECTOR.settings)
        self.status_service = status_service

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
                    await asyncio.create_task(func(payload))

    @async_log
    async def process_return_simple_result_task(self, data: T.Dict[str, T.Any]):
        await self.status_service.change_qa_status(data['uq_id'], status='Sending results.')
        for msg in data['result']:
            await asyncio.sleep(2)
            await self.send_messages([data['user_id']], msg)
        await self.status_service.change_qa_status(data['uq_id'], status='Finished.')

    async def send_messages(self, user_ids: T.List[int], message: str) -> None:
        for user_id in user_ids:
            await self.bot.send_message(user_id, message)
