import typing as T  # noqa
import asyncio
import json
import logging

from aio_pika import IncomingMessage
from aio_pika.abc import AbstractRobustConnection, ExchangeType

from src.repos.factory import RepoFactory


class RabbitMQWorkerFactory:
    def __init__(
        self,
        repo: RepoFactory,
        connection_pool: AbstractRobustConnection,
        queues_info: T.List[T.Tuple[str, str]],
        exchange_name: str = 'direct',
    ):
        self.repo = repo
        self.connection_pool = connection_pool
        self.exchange_name = exchange_name
        self.queues_info = queues_info

    async def start_listening(self, async_funcs: T.Dict[str, T.Callable[..., T.Awaitable[None]]]):
        async with self.connection_pool, self.connection_pool.channel() as channel:
            exchange = await channel.declare_exchange(self.exchange_name, type=ExchangeType.DIRECT, auto_delete=True)
            queues = []

            for queue_name, routing_key in self.queues_info:
                queue = await channel.declare_queue(queue_name, auto_delete=True)
                await queue.bind(exchange=exchange, routing_key=routing_key)
                logging.info(f'{queue_name}:{routing_key} --> Worker is healthy')
                task = self.process_queue(queue, async_funcs)
                queues.append(task)

            await asyncio.gather(*queues)

    async def process_queue(self, queue, async_funcs):
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                await self.handle_message(message, async_funcs)

    @staticmethod
    async def handle_message(message: IncomingMessage, async_funcs: T.Dict[str, T.Callable[..., T.Awaitable[None]]]):
        payload = json.loads(message.body)
        payload['priority'] = message.priority
        routing_key = message.routing_key
        logging.info(f'Received message with routing_key {routing_key}: {payload}')

        if routing_key in async_funcs:
            await asyncio.create_task(async_funcs[routing_key](payload))
        else:
            logging.warning(f'No handler for routing_key {routing_key}')

        await message.ack()
