from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from src.bot.handlers.defaults.menu_default import answer_menu
from src.bot.injector import INJECTOR
from src.services.factories.tg_bot import TgBotService

router = Router(name=__name__)


@router.message(CommandStart(), INJECTOR.inject_tg_bot)
async def command_start_handler(message: Message, tg_bot_service: TgBotService) -> None:
    await tg_bot_service.get_or_create_tg_user(message.from_user.id, message.from_user.username)
    await answer_menu(message)
