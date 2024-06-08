from aiogram import Router, F, types

from src.bot.handlers.defaults.menu_default import answer_menu

router = Router(name=__name__)


@router.callback_query(F.data == 'menu')
async def menu_callback(callback: types.CallbackQuery):
    await callback.answer()
    await answer_menu(callback.message)
