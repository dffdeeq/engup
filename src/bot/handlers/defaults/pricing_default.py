import typing as T  # noqa

from aiogram.types import InlineKeyboardButton, Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.postgres.models.tg_user import TgUser


async def get_pricing(user: TgUser) -> T.Tuple[str, InlineKeyboardBuilder]:
    text = ('Premium points (priority processing of requests)\n'
            f'You have: {user.pts} points\n\n'
            'Choose how many points to buy')
    builder = InlineKeyboardBuilder([
        [
            InlineKeyboardButton(text='10 - 300р.', callback_data='not implemented'),
            InlineKeyboardButton(text='50 - 1400р.', callback_data='not implemented'),
         ],
    ])
    return text, builder


async def answer_pricing(instance: T.Union[Message, CallbackQuery], user: TgUser) -> None:
    text, builder = await get_pricing(user)
    if isinstance(instance, CallbackQuery):
        await instance.message.edit_text(text, reply_markup=builder.as_markup())
    else:
        await instance.answer(text, reply_markup=builder.as_markup())
