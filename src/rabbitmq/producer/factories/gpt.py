import json
import typing as T  # noqa

from aio_pika import Message

from src.libs.adapter import Adapter
from src.libs.factories.gpt.models.result import Result
from src.postgres.enums import CompetenceEnum
from src.rabbitmq.producer.factory import RabbitMQProducerFactory


class GPTProducer(RabbitMQProducerFactory):
    def __init__(self, dsn_string: str, adapter: Adapter, exchange_name: str = 'direct'):
        super().__init__(dsn_string=dsn_string, adapter=adapter, exchange_name=exchange_name)

    async def create_task_generate_result(
        self,
        uq_id: int,
        premium_queue: bool = False
    ):
        message = Message(
            body=bytes(json.dumps({'uq_id': uq_id}), 'utf-8'),
            content_type='json',
        )
        await self._publish(
            message,
            'gpt_generate_result_use_local_model',
            priority=self.get_priority(premium_queue)
        )

    async def create_task_return_result_to_user(
        self,
        user_id: int,
        result: Result,
        competence: CompetenceEnum,
        premium_queue: bool = False,
    ):
        message = Message(
            body=bytes(json.dumps({
                'user_id': user_id,
                'result': result.model_dump(),
                'competence': competence
            }), 'utf-8'),
            content_type='json',
        )
        await self._publish(
            message,
            'tg_bot_return_result_to_user',
            priority=self.get_priority(premium_queue)
        )

    async def create_task_return_simple_result_to_user(
        self,
        user_id: int,
        result: T.List[str],
        premium_queue: bool = False
    ):
        message = Message(
            body=bytes(json.dumps({'user_id': user_id, 'result': result}), 'utf-8'),
            content_type='json',
        )
        await self._publish(
            message,
            'tg_bot_return_simple_result_to_user',
            priority=self.get_priority(premium_queue)
        )
