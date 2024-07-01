import json
import os.path
import typing as T  # noqa

from aio_pika import Message

from src.libs.adapter import Adapter
from src.rabbitmq.producer.factory import RabbitMQProducerFactory
from src.settings.static import TEMP_FILES_DIR


class ApiHostProducer(RabbitMQProducerFactory):
    def __init__(self, dsn_string: str, adapter: Adapter, exchange_name: str = 'direct'):
        super().__init__(dsn_string=dsn_string, adapter=adapter, exchange_name=exchange_name)

    async def create_task_send_to_transcription(self, filenames: T.List[str], premium_queue: bool = False):
        message = Message(
            body=bytes(json.dumps({'files': [os.path.join(TEMP_FILES_DIR, f) for f in filenames]}), 'utf-8'),
            content_type='json',
        )
        await self._publish(message, 'apihost_to_transcription', priority=self.get_priority(premium_queue))

    async def create_task_update_answers(
        self,
        answers_and_filenames: T.List[T.Dict[str, str]],
        premium_queue: bool = False
    ):
        message = Message(
            body=bytes(json.dumps({'filenames': answers_and_filenames}), 'utf-8'),
            content_type='json',
        )
        await self._publish(message, 'apihost_update_answers', priority=self.get_priority(premium_queue))
