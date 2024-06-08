from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext

from src.bot.injector import INJECTOR
from src.services.factories.gpt import GPTService
from src.services.factories.tg_bot import TgBotService

router = Router(name=__name__)


@router.callback_query(F.data == 'writing', INJECTOR.inject_tg_bot, INJECTOR.inject_gpt)
async def writing_start(
    callback: types.CallbackQuery,
    state: FSMContext,
    tg_bot_service: TgBotService,
    gpt_service: GPTService,
):
    await callback.answer(text='This feature is under development', show_alert=True)
