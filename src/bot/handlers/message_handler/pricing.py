from aiogram import Router, F, types

from src.bot.handlers.defaults.pricing_default import answer_pricing

router = Router(name=__name__)


@router.callback_query(F.data == 'pricing')
async def pricing_callback(callback: types.CallbackQuery):
    await callback.answer()
    await answer_pricing(callback.message)
