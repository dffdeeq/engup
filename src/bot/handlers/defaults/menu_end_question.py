import typing as T  # noqa

from aiogram.types import InlineKeyboardButton, Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.bot.constants import DefaultMessages
from src.postgres.enums import CompetenceEnum


async def get_menu_for_user_without_pts_and_sub() -> T.Tuple[str, InlineKeyboardBuilder]:
    text = DefaultMessages.DONT_HAVE_POINTS
    builder = InlineKeyboardBuilder([
        [InlineKeyboardButton(text='Buy', callback_data='pricing')],
    ])
    return text, builder


async def answer_menu_for_user_without_pts_and_sub(instance: T.Union[Message, CallbackQuery]) -> None:
    text, builder = await get_menu_for_user_without_pts_and_sub()
    if isinstance(instance, CallbackQuery):
        await instance.message.edit_text(text, reply_markup=builder.as_markup())
    else:
        await instance.answer(text, reply_markup=builder.as_markup())


async def get_menu_for_user_with_pts_or_sub(
    competence:
    CompetenceEnum,
    method: str
) -> T.Tuple[str, InlineKeyboardBuilder]:
    text = DefaultMessages.HAVE_POINTS
    builder = InlineKeyboardBuilder([
        [InlineKeyboardButton(text='Continue', callback_data=f'confirm_task_{competence.value} {method}')],
    ])
    return text, builder


async def answer_menu_for_user_with_pts_or_sub(
    instance: T.Union[Message, CallbackQuery],
    competence: CompetenceEnum,
    method: str
) -> None:
    text, builder = await get_menu_for_user_with_pts_or_sub(competence, method)
    if isinstance(instance, CallbackQuery):
        await instance.message.edit_text(text, reply_markup=builder.as_markup())
    else:
        await instance.answer(text, reply_markup=builder.as_markup())
