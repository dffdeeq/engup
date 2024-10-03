import typing as T  # noqa

from aiogram.types import InlineKeyboardButton, Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder


async def get_dev_menu() -> T.Tuple[str, InlineKeyboardBuilder]:
    text = 'Dev Menu\n----------'
    builder = InlineKeyboardBuilder([
        [
            InlineKeyboardButton(text='Run task', callback_data='dev_run_task_processing default'),
            InlineKeyboardButton(text='Run task premium', callback_data='dev_run_task_processing premium'),
        ],
    ])
    return text, builder


async def answer_dev_menu(instance: T.Union[Message, CallbackQuery]) -> None:
    text, builder = await get_dev_menu()
    if isinstance(instance, CallbackQuery):
        await instance.message.edit_text(text, reply_markup=builder.as_markup())
    else:
        await instance.answer(text, reply_markup=builder.as_markup())
