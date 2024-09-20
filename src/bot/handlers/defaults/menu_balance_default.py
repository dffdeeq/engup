import typing as T  # noqa

from aiogram.types import InlineKeyboardButton, Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.postgres.models.subscription import Subscription
from src.postgres.models.tg_user import TgUser


async def get_balance_menu(
    user: TgUser,
    subscription: T.Optional[Subscription]
) -> T.Tuple[str, InlineKeyboardBuilder]:
    if subscription:
        formatted_date = subscription.end_date.strftime('%d.%m.%Y')
        subscription_text = f'💳 <b>Subscription:</b> until {formatted_date}\n'
    else:
        subscription_text = "💳 <b>Subscription:</b> <i>No active subscription</i>\n"
    text = subscription_text + (f'💎 <b>Balance:</b> {user.pts} premium test{"" if user.pts == 1 else "s"}.\n\n'
                                f'Choose an option:')
    builder = InlineKeyboardBuilder([
        [InlineKeyboardButton(text='💳 Buy', callback_data='pricing'), ],
        [InlineKeyboardButton(text='🤝 Get premium tests for free', callback_data='free_tests'), ],
        [InlineKeyboardButton(text='🔙 Back', callback_data='menu'), ],
    ])
    return text, builder


async def answer_balance_menu(
    instance: T.Union[Message, CallbackQuery],
    user: TgUser,
    subscription: T.Optional[Subscription]
) -> None:
    text, builder = await get_balance_menu(user, subscription)
    if isinstance(instance, CallbackQuery):
        await instance.message.edit_text(text, reply_markup=builder.as_markup())
    else:
        await instance.answer(text, reply_markup=builder.as_markup())
