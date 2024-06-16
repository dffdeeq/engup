import typing as T  # noqa
import aio_pika

from aio_pika import Message
from aio_pika.abc import AbstractRobustConnection, AbstractRobustChannel, AbstractRobustExchange

from src.libs.adapter import Adapter


class RabbitMQProducerFactory:
    def __init__(self, dsn_string: str, exchange_name: str, adapter: Adapter):
        """
        RabbitMQ Producer Base Class.
        :param dsn_string: Connection string for RabbitMQ.
        :param exchange_name: Name of the exchange to use.
        :param adapter: Adapter instance.
        """
        self.dsn_string: str = dsn_string
        self.exchange_name: str = exchange_name
        self.adapter: Adapter = adapter
        self._rabbitmq_pool: T.Optional[AbstractRobustConnection] = None
        self._channel: T.Optional[AbstractRobustChannel] = None
        self._exchange: T.Optional[AbstractRobustExchange] = None

    async def _publish(self, message: Message, routing_key: str):
        await self.__ensure_connection_and_channel()
        exchange = await self.__get_exchange()
        await exchange.publish(message, routing_key=routing_key)

    async def __ensure_connection_and_channel(self):
        if not self._rabbitmq_pool:
            self._rabbitmq_pool = await aio_pika.connect_robust(url=self.dsn_string)
        if not self._channel or self._channel.is_closed:
            self._channel = await self._rabbitmq_pool.channel()

    async def __get_exchange(self):
        if not self._exchange:
            self._exchange = await self._channel.declare_exchange(self.exchange_name, auto_delete=True)
        return self._exchange
