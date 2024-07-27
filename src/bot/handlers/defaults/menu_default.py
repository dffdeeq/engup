import typing as T  # noqa

from aiogram.types import InlineKeyboardButton, Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder


async def get_menu() -> T.Tuple[str, InlineKeyboardBuilder]:
    text = 'Please select a test to practice'
    builder = InlineKeyboardBuilder([
        [InlineKeyboardButton(text='📚 Start preparing for IELTS', callback_data='ielts_menu')],
        [InlineKeyboardButton(text='💎 Balance', callback_data='balance')],
        [InlineKeyboardButton(text='❓ Support', callback_data='support_menu')],
    ])
    return text, builder


async def answer_menu(instance: T.Union[Message, CallbackQuery]) -> None:
    text, builder = await get_menu()
    if isinstance(instance, CallbackQuery):
        await instance.message.edit_text(text, reply_markup=builder.as_markup())
    else:
        await instance.answer(text, reply_markup=builder.as_markup())
