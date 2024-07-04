import typing as T  # noqa

from aiogram.types import InlineKeyboardButton, Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder


async def get_balance(user_points: int) -> T.Tuple[str, InlineKeyboardBuilder]:
    text = f'You have {user_points} points.\n\nPoints give you the advantage of priority processing for your results.'
    builder = InlineKeyboardBuilder([
        [
            InlineKeyboardButton(text='Purchase', callback_data='pricing'),
         ],
        [
            InlineKeyboardButton(text='Return', callback_data='menu'),
        ]
    ])
    return text, builder


async def answer_balance(instance: T.Union[Message, CallbackQuery], user_points) -> None:
    text, builder = await get_balance(user_points)
    if isinstance(instance, CallbackQuery):
        await instance.message.edit_text(text, reply_markup=builder.as_markup())
    else:
        await instance.answer(text, reply_markup=builder.as_markup())
