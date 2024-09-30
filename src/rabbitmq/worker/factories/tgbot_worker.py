import json
import logging
import typing as T  # noqa
import asyncio
from functools import wraps

from aio_pika import Message
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.bot.constants import DefaultMessages
from src.bot.core.bot import get_bot
from src.bot.injector import INJECTOR
from src.rabbitmq.worker.factory import RabbitMQWorkerFactory
from src.repos.factories.temp_data import TempDataRepo
from src.services.factories.status_service import StatusService
from src.settings import Settings

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
        dsn_string: str,
        settings: Settings,
        queue_name: str,
        status_service: StatusService,
    ):
        super().__init__(repo, dsn_string, queue_name)
        self.repo = repo
        self.session = session
        self.settings = settings
        self.bot = get_bot(INJECTOR.settings)
        self.status_service = status_service

    @staticmethod
    async def handle_message(message: Message, func: T.Callable):
        payload = json.loads(message.body)  # noqa
        payload['priority'] = message.priority  # noqa
        logger.info(f'Received {str(payload)[:50]}')
        await asyncio.create_task(func(payload))

    @async_log
    async def process_return_simple_result_task(self, data: T.Dict[str, T.Any]):
        await self.status_service.change_qa_status(data['uq_id'], status='Sending results.')
        for msg in data['result']:
            await asyncio.sleep(2)
            logger.info(msg)
            await self.send_messages([data['user_id']], msg)

        if data['bad_pronunciation']:
            msg, builder = self.get_pronunciation_mini_app()
            await self.bot.send_message(data['user_id'], msg, reply_markup=builder.as_markup())

        if data['less_than_three_points']:
            msg, builder = self.get_less_than_three_points_msg_and_keyboard()
            await self.bot.send_message(data['user_id'], msg, reply_markup=builder.as_markup())
        else:
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text='Menu', callback_data='menu'), ],
            ])
            await self.bot.send_message(data['user_id'], 'Sending results is complete.', reply_markup=keyboard)

        await self.status_service.change_qa_status(data['uq_id'], status='Finished.')

    async def send_messages(self, chat_ids: T.List[int], message: str) -> None:
        for user_id in chat_ids:
            await self.bot.send_message(user_id, message)

    async def log_error_into_support_group(self, data: T.Dict[str, T.Any]):
        error_text = data['error_text']
        await self.send_messages([self.settings.bot.support_group_id, ], error_text)

    def get_pronunciation_mini_app(self) -> T.Tuple[str, InlineKeyboardBuilder]:
        text = DefaultMessages.BAD_PRONUNCIATION_ALERT
        builder = InlineKeyboardBuilder([
            [
                InlineKeyboardButton(
                    text="Open Mini App",
                    web_app=WebAppInfo(url=self.settings.bot.mini_app_pronunciation_url))
            ]
        ])
        return text, builder

    @staticmethod
    def get_less_than_three_points_msg_and_keyboard() -> T.Tuple[str, InlineKeyboardBuilder]:
        text = DefaultMessages.LOW_POINTS_BALANCE_ALERT
        builder = InlineKeyboardBuilder([
            [InlineKeyboardButton(text='Buy', callback_data='pricing'), ],
            [InlineKeyboardButton(text='Recommend/Share', callback_data='free_tests'), ],
            [InlineKeyboardButton(text='Leave Feedback', callback_data='take_the_survey')],
            [InlineKeyboardButton(text='Menu', callback_data='menu'), ],
        ])
        return text, builder
