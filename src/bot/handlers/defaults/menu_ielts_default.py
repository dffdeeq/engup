import typing as T  # noqa

from aiogram.types import InlineKeyboardButton, Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder


async def get_ielts_menu() -> T.Tuple[str, InlineKeyboardBuilder]:
    text = '📚 Start preparing for IELTS. Choose a task type:'
    builder = InlineKeyboardBuilder([
        [InlineKeyboardButton(text='🎙️ Speaking tasks', callback_data='speaking')],
        [InlineKeyboardButton(text='📝 Writing tasks', callback_data='writing')],
        [InlineKeyboardButton(text='🔙 Back', callback_data='menu')],
    ])
    return text, builder


async def answer_ielts_menu(instance: T.Union[Message, CallbackQuery]) -> None:
    text, builder = await get_ielts_menu()
    if isinstance(instance, CallbackQuery):
        await instance.message.edit_text(text, reply_markup=builder.as_markup())
    else:
        await instance.answer(text, reply_markup=builder.as_markup())
