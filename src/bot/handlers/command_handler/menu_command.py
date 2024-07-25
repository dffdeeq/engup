from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from src.bot.handlers.defaults.menu_default import get_menu
from src.bot.injector import INJECTOR
from src.services.factories.tg_user import TgUserService

router = Router(name=__name__)


@router.message(Command('menu'), INJECTOR.inject_tg_user)
async def command_menu_handler(message: Message, tg_user_service: TgUserService, state: FSMContext) -> None:
    await state.clear()

    await tg_user_service.get_or_create_tg_user(message.from_user.id, message.from_user.username)
    text, builder = await get_menu()
    await message.answer(text, reply_markup=builder.as_markup())
