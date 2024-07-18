from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext

from src.bot.core.states import AdminState
from src.bot.injector import INJECTOR
from src.rabbitmq.producer.factories.gpt import GPTProducer

router = Router(name=__name__)


@router.callback_query(F.data == 'admin_run_task_processing', INJECTOR.inject_tg_user)
async def admin_run_task_processing(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(AdminState.get_uq_id)
    await callback.message.edit_text(text='Enter uq_id')


@router.message(AdminState.get_uq_id, INJECTOR.inject_gpt_producer)
async def speaking_first_part(message: types.Message, gpt_producer: GPTProducer):
    try:
        uq_id = int(message.text)
    except ValueError:
        await message.answer(text='uq_id must be an integer')
        return

    await gpt_producer.create_task_generate_result(uq_id, premium_queue=True)
    await message.answer(text='Successful')
