from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext

from src.bot.core.states import AdminState
from src.bot.injector import INJECTOR
from src.rabbitmq.producer.factories.gpt import GPTProducer

router = Router(name=__name__)


@router.callback_query(F.data.startswith('admin_run_task_processing'), INJECTOR.inject_tg_user)
async def admin_run_task_processing(callback: types.CallbackQuery, state: FSMContext):
    processing_option = callback.data.split()[1]
    prem = False
    if processing_option == 'premium':
        prem = True
    await state.set_state(AdminState.get_uq_id)
    await state.set_data({'premium': prem})
    await callback.message.edit_text(text='Enter uq_id')


@router.message(AdminState.get_uq_id, INJECTOR.inject_gpt_producer)
async def speaking_first_part(message: types.Message, state: FSMContext, gpt_producer: GPTProducer):
    try:
        uq_id = int(message.text)
    except ValueError:
        await message.answer(text='uq_id must be an integer')
        return

    premium_queue = (await state.get_data())['premium']

    await gpt_producer.create_task_generate_result(uq_id, premium_queue=premium_queue)
    await message.answer(text='Successful')
