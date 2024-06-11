import typing as T  # noqa

from aiogram.types import InlineKeyboardButton, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder


async def get_pricing() -> T.Tuple[str, InlineKeyboardBuilder]:
    text = ('Premium points (priority processing of requests)\n'
            'You have: 0 points\n\n'
            'Choose how many points to buy')
    builder = InlineKeyboardBuilder([
        [
            InlineKeyboardButton(text='10 - 300р.', callback_data='not implemented'),
            InlineKeyboardButton(text='50 - 1400р.', callback_data='not implemented'),
         ],
    ])
    return text, builder


async def answer_pricing(msg: Message) -> None:
    text, builder = await get_pricing()
    await msg.answer(text, reply_markup=builder.as_markup())
