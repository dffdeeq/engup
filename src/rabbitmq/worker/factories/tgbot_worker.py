import logging
import typing as T  # noqa
import asyncio
from functools import wraps

from aio_pika.abc import AbstractRobustConnection
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.bot.core.bot import get_bot
from src.bot.handlers.constants import MessageTemplates, Constants
from src.bot.handlers.utils import answer_parts_async_generator
from src.bot.injector import INJECTOR
from src.libs.factories.gpt.models.result import Result
from src.postgres.enums import CompetenceEnum
from src.rabbitmq.worker.factory import RabbitMQWorkerFactory
from src.repos.factories.temp_data import TempDataRepo


logging.basicConfig(level=logging.INFO)
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
        connection_pool: AbstractRobustConnection,
        queues_info: T.List[T.Tuple[str, str]],
    ):
        super().__init__(repo, connection_pool, queues_info)
        self.repo = repo
        self.session = session
        self.bot = get_bot(INJECTOR.settings)

    @async_log
    async def process_return_simple_result_task(self, data: T.Dict[str, T.Any]):
        for msg in data['result']:
            await asyncio.sleep(2)
            await self.send_messages([data['user_id']], msg)

    @async_log
    async def process_return_result_task(self, data: T.Dict[str, T.Any]):
        await self.send_result_to_user(data['user_id'], data['result'], data['competence'])

    async def send_result_to_user(self, user_id: int, result: dict, competence: CompetenceEnum):
        result = Result.parse_obj(result)
        async for msg in answer_parts_async_generator(result, competence):
            await self.bot.send_message(user_id, text=msg)
            await asyncio.sleep(3)

        general_recommendations = MessageTemplates.GENERAL_RECOMMENDATIONS_TEMPLATE.format(
            vocabulary='\n'.join(f'- {word}' for word in result.vocabulary),
            practice_regularly=Constants.PRACTICE_REGULARLY_DICT[competence]
        )
        await self.bot.send_message(user_id, text=general_recommendations)

    async def send_messages(self, user_ids: T.List[int], message: str) -> None:
        for user_id in user_ids:
            await self.bot.send_message(user_id, message)
