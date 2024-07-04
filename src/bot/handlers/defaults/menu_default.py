import typing as T  # noqa

from aiogram.types import InlineKeyboardButton, Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder


async def get_menu() -> T.Tuple[str, InlineKeyboardBuilder]:
    text = 'Please select a test to practice'
    builder = InlineKeyboardBuilder([
        [
            InlineKeyboardButton(text='Speaking', callback_data='speaking'),
            InlineKeyboardButton(text='Writing', callback_data='writing')
         ],
        [
            InlineKeyboardButton(text='Balance', callback_data='balance'),
            InlineKeyboardButton(text='Pricing', callback_data='pricing')
        ],
    ])
    return text, builder


async def answer_menu(instance: T.Union[Message, CallbackQuery]) -> None:
    text, builder = await get_menu()
    if isinstance(instance, CallbackQuery):
        await instance.message.edit_text(text, reply_markup=builder.as_markup())
    else:
        await instance.answer(text, reply_markup=builder.as_markup())
