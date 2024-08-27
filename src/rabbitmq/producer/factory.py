import asyncio
import logging
import typing as T  # noqa
import aio_pika

from aio_pika import Message
from aio_pika.abc import AbstractRobustConnection, AbstractRobustChannel, AbstractRobustExchange
from aiormq import AMQPConnectionError, AMQPChannelError

from src.libs.adapter import Adapter

logger = logging.getLogger(__name__)


class RabbitMQProducerFactory:
    def __init__(
        self,
        dsn_string: str,
        adapter: Adapter,
        exchange_name: str = 'direct',
        max_retries: int = 5,
        retry_delay: float = 2.0
    ):
        """
        RabbitMQ Producer Base Class.
        :param dsn_string: Connection string for RabbitMQ.
        :param adapter: Adapter instance.
        :param exchange_name: Name of the exchange to use.
        """
        self.dsn_string: str = dsn_string
        self.adapter: Adapter = adapter
        self.exchange_name: str = exchange_name
        self._rabbitmq_pool: T.Optional[AbstractRobustConnection] = None
        self._channel: T.Optional[AbstractRobustChannel] = None
        self._exchange: T.Optional[AbstractRobustExchange] = None

        self.connection_max_retries: int = max_retries
        self.connection_retry_delay: float = retry_delay

    async def _publish(self, message: Message, routing_key: str, priority: int = 0):
        channel = await self.__get_channel()
        exchange = await self.__get_exchange(channel)
        message.priority = priority
        await exchange.publish(message, routing_key=routing_key)
        logger.info(f"Message published to {routing_key} with priority {priority}")

    async def __get_channel(self):
        retries = 0
        while retries < self.connection_max_retries:
            try:
                if not self._rabbitmq_pool or self._rabbitmq_pool.is_closed:
                    logger.info("Connecting to RabbitMQ...")
                    self._rabbitmq_pool = await aio_pika.connect_robust(url=self.dsn_string)

                if self._channel and self._channel.is_closed:
                    await self._channel.close()

                self._channel = await self._rabbitmq_pool.channel()
                if self._channel.is_closed:
                    raise AMQPChannelError("Channel is closed after opening.")
                return self._channel
            except (AMQPConnectionError, AMQPChannelError) as e:
                retries += 1
                logger.error(f"Connection attempt {retries} failed: {e}")
                if retries < self.connection_max_retries:
                    delay = self.connection_retry_delay * (2 ** retries)
                    logger.info(f"Retrying connection in {delay} seconds...")
                    await asyncio.sleep(delay)
                else:
                    logger.critical("Max retries reached, failed to establish connection.")
                    raise

    async def __get_exchange(self, channel):
        if not self._exchange:
            logger.info(f"Declaring exchange {self.exchange_name}...")
            self._exchange = await channel.declare_exchange(self.exchange_name)
        return self._exchange

    @staticmethod
    def get_priority(premium_queue: bool):
        return 5 if premium_queue else 0
