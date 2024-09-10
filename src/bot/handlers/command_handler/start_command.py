import logging
import uuid

from aiogram import Router
from aiogram.filters import CommandStart, CommandObject
from aiogram.types import Message, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.bot.constants import DefaultMessages
from src.bot.injector import INJECTOR
from src.services.factories.metrics import MetricsService
from src.services.factories.tg_user import TgUserService

router = Router(name=__name__)


@router.message(
    CommandStart(),
    INJECTOR.inject_tg_user,
    INJECTOR.inject_metrics_service
)
async def command_start_handler(
    message: Message,
    command: CommandObject,
    tg_user_service: TgUserService,
    metrics_service: MetricsService
) -> None:
    user_referrer_id = None
    command_args = command.args
    umt_data_dict = {}

    if command_args:
        user = await tg_user_service.repo.get_tg_user_by_tg_id(message.from_user.id)
        if not user:
            try:
                try:
                    metrics_uuid = uuid.UUID(command_args)
                    metrics_data = await metrics_service.get_metrics_data(metrics_uuid)
                    metrics_string = metrics_data.metrics_string.split('__')
                    logging.info(f'args: {metrics_string}')
                    for item in metrics_string:
                        key, value = item.split("=")
                        umt_data_dict[key] = value

                    await tg_user_service.adapter.analytics_client.send_event(
                        str(uuid.uuid4()),
                        event_name='conversion_event_signup',
                        umt_data_dict=umt_data_dict
                    )

                except ValueError:
                    referral = await tg_user_service.repo.get_tg_user_by_tg_id(int(command_args))
                    if referral:
                        user_referrer_id = referral.id
            except Exception as e:
                logging.error(e)

    await tg_user_service.get_or_create_tg_user(
        message.from_user.id, message.from_user.username, user_referrer_id, umt_data_dict
    )
    builder = InlineKeyboardBuilder([
        [InlineKeyboardButton(text='📚 Start preparing for IELTS', callback_data='ielts_menu')],
    ])
    await message.answer(text=DefaultMessages.START_MESSAGE, reply_markup=builder.as_markup())
