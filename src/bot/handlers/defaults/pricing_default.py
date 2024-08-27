import typing as T  # noqa

from aiogram.types import InlineKeyboardButton, Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.postgres.models.tg_user import TgUser


async def get_pricing(user: TgUser) -> T.Tuple[str, InlineKeyboardBuilder]:
    text = ('Premium tests (priority processing of requests)\n'
            f'You have: {user.pts} premium test{"" if user.pts == 1 else "s"}\n\n'
            'Choose how many premium tests to buy')
    builder = InlineKeyboardBuilder([
            [InlineKeyboardButton(
                text='💸 Package of 3 premium tests – 150 ⭐', callback_data='buy_pts_by_tg_stars 3'),],
            [InlineKeyboardButton(
                text='💸 Package of 10 premium tests – 450 ⭐', callback_data='buy_pts_by_tg_stars 10'),],
            [InlineKeyboardButton(
                text='💸 Package of 100 premium tests – 4000 ⭐', callback_data='buy_pts_by_tg_stars 100'),],
            [InlineKeyboardButton(
                text='🔙 Back', callback_data='balance_menu'),]
    ])
    return text, builder


async def answer_pricing(instance: T.Union[Message, CallbackQuery], user: TgUser) -> None:
    text, builder = await get_pricing(user)
    if isinstance(instance, CallbackQuery):
        await instance.message.edit_text(text, reply_markup=builder.as_markup())
    else:
        await instance.answer(text, reply_markup=builder.as_markup())
