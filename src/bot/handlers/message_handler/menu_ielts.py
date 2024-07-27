from aiogram import Router, F, types

from src.bot.handlers.defaults.ielts_menu_default import answer_ielts_menu
from src.bot.injector import INJECTOR
from src.services.factories.tg_user import TgUserService

router = Router(name=__name__)


@router.callback_query(F.data == 'ielts_menu', INJECTOR.inject_tg_user)
async def ielts_menu_callback(callback: types.CallbackQuery, tg_user_service: TgUserService):
    await tg_user_service.mark_user_activity(callback.from_user.id, 'go to ielts menu')

    await callback.answer()
    await answer_ielts_menu(callback)
