import typing as T  # noqa

from aiogram.types import InlineKeyboardButton, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder


async def get_menu() -> T.Tuple[str, InlineKeyboardBuilder]:
    text = 'Please select a test to practice'
    builder = InlineKeyboardBuilder([
        [InlineKeyboardButton(text='Speaking', callback_data='speaking')],
        [InlineKeyboardButton(text='Writing', callback_data='writing')]
    ])
    return text, builder


async def answer_menu(msg: Message) -> None:
    text, builder = await get_menu()
    await msg.answer(text, reply_markup=builder.as_markup())
