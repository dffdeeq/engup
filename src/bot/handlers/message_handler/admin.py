import json

from aio_pika import Message
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy import select

from src.bot.core.states import AdminState
from src.bot.injector import INJECTOR
from src.postgres.models.tg_user import TgUser
from src.rabbitmq.producer.factories.mp3tts import MP3TTSProducer
from src.services.factories.tg_user import TgUserService

router = Router(name=__name__)


@router.callback_query(F.data.startswith('admin_start_send_msg'), INJECTOR.inject_tg_user)
async def admin_start_send_msg(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(AdminState.get_mailing_users_list)
    await callback.message.edit_text(text='Specify the user IDs separated by a space\n'
                                          '(Or use "all" to send to all users)')


@router.message(AdminState.get_mailing_users_list, INJECTOR.inject_tg_user)
async def admin_get_mailing_users_list(message: types.Message, state: FSMContext, tg_user_service: TgUserService):
    arg = message.text
    if arg == 'all':
        async with tg_user_service.session() as session:
            users_query = select(TgUser.id)
            result = await session.execute(users_query)
            users_list = result.scalars().all()
    else:
        try:
            users_list = list(map(int, arg.split()))
        except ValueError:
            await message.answer(text='Your message should contain only user IDs separated by a space')
            return

    await state.set_state(AdminState.get_mailing_msg)
    await state.update_data({'users_list': users_list})
    await message.answer(text='Enter a message to send')


@router.message(AdminState.get_mailing_msg, INJECTOR.inject_tg_user)
async def admin_get_mailing_msg(message: types.Message, state: FSMContext, tg_user_service: TgUserService):
    text = message.text
    state_data = await state.get_data()
    users_list = state_data['users_list']
    await state.update_data({'mailing_msg': text})

    builder = InlineKeyboardBuilder([[InlineKeyboardButton(text='Confirm', callback_data='admin_send_msg_confirm')]])

    if users_list == 'all':
        async with tg_user_service.session() as session:
            users_query = select(TgUser.id)
            result = await session.execute(users_query)
            users_list = result.scalars().all()

    text = f'{len(users_list)} users will receive the following message:\n\n{text}'
    await message.answer(text=text, reply_markup=builder.as_markup())


@router.callback_query(F.data.startswith('admin_send_msg_confirm'), INJECTOR.inject_apihost_producer)
async def admin_send_msg_confirm(callback: types.CallbackQuery, state: FSMContext, apihost_producer: MP3TTSProducer):
    state_data = await state.get_data()
    msg = Message(
        body=bytes(json.dumps({
            'text': state_data['mailing_msg'],
            'users_list': state_data['users_list'],
            'sender_id': callback.from_user.id,
        }),
            'utf-8'),
        content_type='json',
    )
    await apihost_producer.publish(message=msg, routing_key='tg_bot_mailing')
    await callback.message.edit_text(text='Successful')
