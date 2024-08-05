from aiogram import Router, F, types

from src.bot.handlers.defaults.menu_balance_default import answer_balance_menu
from src.bot.injector import INJECTOR
from src.services.factories.tg_user import TgUserService

router = Router(name=__name__)


@router.callback_query(F.data == 'balance_menu', INJECTOR.inject_tg_user)
async def balance_menu_callback(callback: types.CallbackQuery, tg_user_service: TgUserService):
    user = await tg_user_service.get_or_create_tg_user(callback.from_user.id, callback.from_user.username)
    await tg_user_service.mark_user_activity(callback.from_user.id, 'go to balance menu')

    await callback.answer()
    await answer_balance_menu(callback, user)
