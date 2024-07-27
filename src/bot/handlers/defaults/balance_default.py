import typing as T  # noqa

from aiogram.types import InlineKeyboardButton, Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.postgres.models.tg_user import TgUser


async def get_balance_menu(user: TgUser) -> T.Tuple[str, InlineKeyboardBuilder]:
    text = f'💎 <b>Balance:</b> {user.pts} tests.\n\nChoose an option:'
    builder = InlineKeyboardBuilder([
        [InlineKeyboardButton(text='💳 Buy tests', callback_data='pricing'),],
        [InlineKeyboardButton(text='🤝 Free tests', callback_data='free_tests'),],
        [InlineKeyboardButton(text='🔙 Back', callback_data='menu'), ],
    ])
    return text, builder


async def answer_balance_menu(instance: T.Union[Message, CallbackQuery], user: TgUser) -> None:
    text, builder = await get_balance_menu(user)
    if isinstance(instance, CallbackQuery):
        await instance.message.edit_text(text, reply_markup=builder.as_markup())
    else:
        await instance.answer(text, reply_markup=builder.as_markup())
