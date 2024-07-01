from aiogram import Router, F, types

from src.bot.handlers.defaults.pricing_default import answer_pricing
from src.bot.injector import INJECTOR
from src.services.factories.tg_user import TgUserService

router = Router(name=__name__)


@router.callback_query(F.data == 'pricing', INJECTOR.inject_tg_user)
async def pricing_callback(callback: types.CallbackQuery, tg_user_service: TgUserService):
    await callback.answer()

    user = await tg_user_service.get_or_create_tg_user(callback.from_user.id)
    await answer_pricing(callback, user)
