from aiogram import Router
from aiogram.filters import CommandStart, CommandObject
from aiogram.types import Message

from src.bot.handlers.defaults.menu_default import answer_menu
from src.bot.injector import INJECTOR
from src.services.factories.tg_user import TgUserService

router = Router(name=__name__)


@router.message(CommandStart(), INJECTOR.inject_tg_user)
async def command_start_handler(message: Message, command: CommandObject, tg_user_service: TgUserService) -> None:
    user_referrer_id = None
    referrer_id = command.args
    if referrer_id:
        referral = await tg_user_service.repo.get_tg_user_by_tg_id(int(referrer_id))
        if referral:
            user_referrer_id = referral.id
    await tg_user_service.get_or_create_tg_user(message.from_user.id, message.from_user.username, user_referrer_id)
    await answer_menu(message)
