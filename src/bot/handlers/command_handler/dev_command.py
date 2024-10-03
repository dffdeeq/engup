from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from src.bot.handlers.defaults.dev_menu_default import answer_dev_menu
from src.bot.injector import INJECTOR
from src.services.factories.tg_user import TgUserService

router = Router(name=__name__)


@router.message(Command('dev'), INJECTOR.inject_tg_user)
async def command_dev_menu_handler(message: Message, tg_user_service: TgUserService) -> None:
    str_user_id = str(message.from_user.id)
    if str_user_id not in tg_user_service.settings.bot.admin_ids:
        return

    await tg_user_service.get_or_create_tg_user(message.from_user.id, message.from_user.username)
    await answer_dev_menu(message)
