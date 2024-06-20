import asyncio
import logging
import typing as T  # noqa

from aio_pika.abc import AbstractRobustConnection
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.bot.core.bot import get_bot
from src.bot.handlers.constants import MessageTemplates
from src.bot.handlers.utils import answer_parts_async_generator
from src.bot.injector import INJECTOR
from src.libs.factories.gpt.models.result import Result
from src.rabbitmq.worker.factory import RabbitMQWorkerFactory
from src.repos.factories.temp_data import TempDataRepo


class TgBotWorker(RabbitMQWorkerFactory):
    def __init__(
        self,
        session: async_sessionmaker,
        repo: TempDataRepo,
        connection_pool: AbstractRobustConnection,
        queues_info: T.List[T.Tuple[str, str]],
    ):
        super().__init__(repo, connection_pool, queues_info)
        self.repo = repo
        self.session = session
        self.bot = get_bot(INJECTOR.settings)

    async def process_return_result_task(self, data: T.Dict[str, T.Any]):
        logging.info(f'---------- Start of Task {self.process_return_result_task.__name__} ----------')
        await self.send_result_to_user(data['user_id'], data['result'])
        logging.info(f'---------- End of Task {self.process_return_result_task.__name__} ----------')

    async def send_result_to_user(self, user_id: int, result: dict):
        result = Result.parse_obj(result)
        async for msg in answer_parts_async_generator(result):
            await self.bot.send_message(user_id, text=msg)
            await asyncio.sleep(3)

        general_recommendations = MessageTemplates.GENERAL_RECOMMENDATIONS_TEMPLATE.format(
            vocabulary='\n'.join(f'- {word}' for word in result.vocabulary)
        )
        await self.bot.send_message(user_id, text=general_recommendations)

    async def send_message(self, user_ids: T.List[int], message: str) -> None:
        for user_id in user_ids:
            await self.bot.send_message(user_id, message)
