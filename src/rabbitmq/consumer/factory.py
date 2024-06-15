import typing as T  # noqa
import asyncio
import json
import logging

from aio_pika.abc import AbstractRobustConnection, ExchangeType


class RabbitMQWorkerFactory:
    def __init__(
        self,
        connection_pool: AbstractRobustConnection,
        queue_name: str,
        routing_key: str,
        exchange_name: str = 'direct',
    ):
        self.connection_pool = connection_pool
        self.exchange_name = exchange_name
        self.queue_name = queue_name
        self.routing_key = routing_key

    async def start_listening(self, async_func: T.Callable[..., T.Awaitable[None]], *args, **kwargs):
        async with self.connection_pool, self.connection_pool.channel() as channel:
            exchange = await channel.declare_exchange(self.exchange_name, type=ExchangeType.DIRECT, auto_delete=True)
            queue = await channel.declare_queue(self.queue_name, auto_delete=True)
            await queue.bind(exchange=exchange, routing_key=self.routing_key)
            async with queue.iterator() as queue_iter:
                logging.info(f'{self.queue_name}:{self.routing_key} --> Worker is healthy')
                async for message in queue_iter:
                    payload = json.loads(message.body)  # noqa
                    logging.info(str(payload))
                    await asyncio.create_task(async_func(*args, **kwargs))
                    await message.ack()  # noqa
                    await asyncio.sleep(1)
