import asyncio
import json
import logging

import aio_pika
from aio_pika import Message

from src.settings import RabbitMQSettings, Settings


class RabbitMQProducer:
    def __init__(
        self,
        settings: RabbitMQSettings,
        queue_name: str,
        routing_key: str,
        exchange_name: str = 'direct',
    ):
        self.settings = settings
        self.queue_name = queue_name
        self.routing_key = routing_key
        self.exchange_name = exchange_name
        self._rabbitmq_pool = None

    async def send_to_rabbitmq(self, message: dict):
        logging.info(message)
        async with (await self.get_rabbitmq_pool()) as connection:
            async with connection.channel() as channel:
                exchange = await channel.declare_exchange(self.exchange_name, auto_delete=True)
                return await exchange.publish(
                    Message(
                        body=bytes(json.dumps(message), 'utf-8'),
                        content_type='json'
                    ),
                    routing_key=self.routing_key
                )

    async def get_rabbitmq_pool(self):
        if not self._rabbitmq_pool:
            self._rabbitmq_pool = await aio_pika.connect_robust(url=self.settings.dsn)
        return self._rabbitmq_pool


async def main():
    settings = Settings.new()
    producer = RabbitMQProducer(settings.rabbitmq, queue_name='gpt_service', routing_key='text_to_result')
    await producer.send_to_rabbitmq({'msg': 'hello!'})


if __name__ == '__main__':
    asyncio.run(main())
