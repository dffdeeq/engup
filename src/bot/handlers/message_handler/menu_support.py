from aiogram import Router, F, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from src.bot.handlers.defaults.menu_support_default import answer_support_menu
from src.bot.injector import INJECTOR
from src.services.factories.tg_user import TgUserService

router = Router(name=__name__)


@router.callback_query(F.data == 'support_menu', INJECTOR.inject_tg_user)
async def support_menu_callback(callback: types.CallbackQuery, tg_user_service: TgUserService):
    await tg_user_service.mark_user_activity(callback.from_user.id, 'go to support menu')

    await callback.answer()
    await answer_support_menu(callback)


@router.callback_query(F.data == 'user_agreement', INJECTOR.inject_tg_user)
async def user_agreement_menu_callback(callback: types.CallbackQuery, tg_user_service: TgUserService):
    text = 'Here you can view the user agreement:\nhttps://telegra.ph/User-Agreement-08-05'
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='🔙 Back', callback_data='menu'), ],
    ])
    await callback.message.edit_text(text=text, reply_markup=keyboard)


@router.callback_query(F.data == 'contact_support', INJECTOR.inject_tg_user)
async def contact_support_menu_callback(callback: types.CallbackQuery, tg_user_service: TgUserService):
    text = 'Support email: support@ielts-offical.com'
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='🔙 Back', callback_data='support_menu'), ],
    ])
    await callback.message.edit_text(text=text, reply_markup=keyboard)
