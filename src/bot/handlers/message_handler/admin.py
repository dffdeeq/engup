import json

from aio_pika import Message
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext

from src.bot.core.states import AdminState
from src.bot.injector import INJECTOR
from src.rabbitmq.producer.factories.mp3tts import MP3TTSProducer

router = Router(name=__name__)


@router.callback_query(F.data.startswith('admin_start_send_msg'), INJECTOR.inject_tg_user)
async def admin_start_send_msg(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(AdminState.get_mailing_users_list)
    await callback.message.edit_text(text='Specify the user IDs separated by a space\n'
                                          '(Or use "all" to send to all users)')


@router.message(AdminState.get_mailing_users_list)
async def admin_get_mailing_users_list(message: types.Message, state: FSMContext):
    arg = message.text
    if arg != 'all':
        try:
            arg = map(int, arg.split())
        except ValueError:
            await message.answer(text='Your message should contain only user IDs separated by a space')
            return

    await state.set_state(AdminState.get_mailing_msg)
    await state.update_data({'users_list': arg})
    await message.edit_text(text='Enter a message to send')


@router.message(AdminState.get_mailing_msg, INJECTOR.inject_apihost_producer)
async def admin_get_mailing_msg(message: types.Message, state: FSMContext, apihost_producer: MP3TTSProducer):
    text = message.text
    state_data = await state.get_data()
    users_list = state_data['users_list']

    message = Message(
        body=bytes(json.dumps({
            'text': text,
            'users_list': users_list
        }),
            'utf-8'),
        content_type='json',
    )

    await apihost_producer.publish(message=Message(), routing_key='')
