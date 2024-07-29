from aiogram import Router, F, types

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
    await callback.answer(text='Not implemented yet.')


@router.callback_query(F.data == 'contact_support', INJECTOR.inject_tg_user)
async def contact_support_menu_callback(callback: types.CallbackQuery, tg_user_service: TgUserService):
    await callback.answer(text='Not implemented yet.')
