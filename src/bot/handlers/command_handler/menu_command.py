from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from src.bot.handlers.defaults.menu_default import get_menu

router = Router(name=__name__)


@router.message(Command('menu'))
async def command_menu_handler(message: Message) -> None:
    text, builder = await get_menu()
    await message.answer(text, reply_markup=builder.as_markup())
