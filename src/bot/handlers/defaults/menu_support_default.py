import typing as T  # noqa

from aiogram.types import InlineKeyboardButton, Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder


async def get_support_menu() -> T.Tuple[str, InlineKeyboardBuilder]:
    text = '❓ Support. Choose an option:'
    builder = InlineKeyboardBuilder([
            [InlineKeyboardButton(text='About', callback_data='not_implemented'),],
            [InlineKeyboardButton(text='📜 User Agreement', callback_data='user_agreement'),],
            [InlineKeyboardButton(text='🆘 Contact Support', callback_data='contact_support'),],
            [InlineKeyboardButton(text='🔙 Back', callback_data='menu'),]
    ])
    return text, builder


async def answer_support_menu(instance: T.Union[Message, CallbackQuery]) -> None:
    text, builder = await get_support_menu()
    if isinstance(instance, CallbackQuery):
        await instance.message.edit_text(text, reply_markup=builder.as_markup())
    else:
        await instance.answer(text, reply_markup=builder.as_markup())
