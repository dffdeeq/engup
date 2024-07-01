from aiogram import Router, F, types

from src.bot.handlers.defaults.balance_default import answer_balance
from src.bot.injector import INJECTOR
from src.services.factories.tg_user import TgUserService

router = Router(name=__name__)


@router.callback_query(F.data == 'balance', INJECTOR.inject_tg_user)
async def balance_callback(callback: types.CallbackQuery, tg_user_service: TgUserService):
    user = await tg_user_service.get_or_create_tg_user(callback.from_user.id)
    await callback.answer()
    await answer_balance(callback, user.pts)
