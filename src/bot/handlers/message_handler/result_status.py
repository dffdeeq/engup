import logging

from aiogram import Router, F, types

from src.bot.injector import INJECTOR
from src.services.factories.status_service import StatusService

router = Router(name=__name__)


@router.callback_query(F.data.startswith('result_status'), INJECTOR.inject_status)
async def result_status_callback(callback: types.CallbackQuery, status_service: StatusService):
    try:
        uq_id = int(callback.data.split()[1])
    except Exception as e:
        logging.error(e)
        return

    status = await status_service.get_qa_status(uq_id=uq_id)

    await callback.answer(text=status, show_alert=True)
