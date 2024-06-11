from aiogram import Router, F, types

from src.bot.handlers.defaults.menu_default import answer_menu
from src.bot.injector import INJECTOR
from src.services.factories.tg_bot import TgBotService

router = Router(name=__name__)


@router.callback_query(F.data == 'menu', INJECTOR.inject_tg_bot)
async def menu_callback(callback: types.CallbackQuery, tg_bot_service: TgBotService):
    await tg_bot_service.get_or_create_tg_user(callback.from_user.id, callback.from_user.username)
    await callback.answer()
    await answer_menu(callback.message)
