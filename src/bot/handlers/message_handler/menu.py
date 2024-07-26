from aiogram import Router, F, types

from src.bot.handlers.defaults.menu_default import answer_menu
from src.bot.injector import INJECTOR
from src.services.factories.tg_user import TgUserService

router = Router(name=__name__)


@router.callback_query(F.data == 'menu', INJECTOR.inject_tg_user)
async def menu_callback(callback: types.CallbackQuery, tg_user_service: TgUserService):
    await tg_user_service.mark_user_activity(callback.from_user.id, 'go to menu')

    await tg_user_service.get_or_create_tg_user(callback.from_user.id, callback.from_user.username)
    await callback.answer()
    await answer_menu(callback)
