import json
import typing as T  # noqa

from aio_pika import Message

from src.libs.adapter import Adapter
from src.rabbitmq.producer.factory import RabbitMQProducerFactory


class ApiHostProducer(RabbitMQProducerFactory):
    def __init__(self, dsn_string: str, exchange_name: str, routing_key: str, adapter: Adapter):
        super().__init__(dsn_string, exchange_name, routing_key, adapter)

    async def send_to_transcription(self, filepaths: T.List[str]):
        routing_key = 'to_transcription'
        message = Message(
            body=bytes(json.dumps({'files': filepaths}), 'utf-8'),
            content_type='json',
        )
        await self._publish(message, routing_key)
