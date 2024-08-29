from aiogram import Router, F, types
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.bot.injector import INJECTOR
from src.services.factories.tg_user import TgUserService

router = Router(name=__name__)


@router.callback_query(F.data == 'free_tests', INJECTOR.inject_tg_user)
async def free_tests_menu_callback(callback: types.CallbackQuery, tg_user_service: TgUserService):
    await tg_user_service.mark_user_activity(callback.from_user.id, 'go to get premium tests for free')

    user = await tg_user_service.get_or_create_tg_user(callback.from_user.id)
    text = f'You have <b>{user.pts}</b> premium tests\n\nHere you can get premium tests for free'
    builder = InlineKeyboardBuilder([
        [InlineKeyboardButton(text='👋 Invite a friend', callback_data='referral'), ],
        [InlineKeyboardButton(text='⭐️ Take the survey', callback_data='leave_feedback'), ],
        [InlineKeyboardButton(text='🔙 Back', callback_data='balance_menu'), ],
    ])

    await callback.message.edit_text(text=text, reply_markup=builder.as_markup())
