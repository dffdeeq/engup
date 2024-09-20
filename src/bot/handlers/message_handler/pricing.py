import json
import logging
import uuid

from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.types import LabeledPrice, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.bot.handlers.defaults.menu_default import answer_menu
from src.bot.handlers.defaults.pricing_default import answer_pricing
from src.bot.injector import INJECTOR
from src.services.factories.subscription import SubscriptionService
from src.services.factories.tg_user import TgUserService

router = Router(name=__name__)


@router.callback_query(F.data == 'not_implemented', INJECTOR.inject_tg_user)
async def not_implemented(callback: types.CallbackQuery):
    await callback.answer(text='Not implemented yet.', show_alert=True)


@router.callback_query(F.data == 'pricing', INJECTOR.inject_tg_user)
async def pricing_callback(callback: types.CallbackQuery, tg_user_service: TgUserService):
    await callback.answer()
    await tg_user_service.mark_user_activity(callback.from_user.id, 'go to buy premium tests')

    user = await tg_user_service.get_or_create_tg_user(callback.from_user.id)
    await answer_pricing(callback, user)


@router.callback_query(F.data.startswith('buy_by_tg_stars'), INJECTOR.inject_tg_user)
async def buy_pts_by_tg_start(callback: types.CallbackQuery, tg_user_service: TgUserService):
    await callback.answer()

    method, amount = callback.data.split()[1:3]
    if method == 'pts':
        price = {
            3: [LabeledPrice(label="3 PTs", amount=150)],
            10: [LabeledPrice(label="10 PTs", amount=450)],
            100: [LabeledPrice(label="100 PTs", amount=4000)]
        }
    elif method == 'month_sub':
        price = {
            1: [LabeledPrice(label="1 month", amount=1)],
            3: [LabeledPrice(label="3 month", amount=4000)],
            6: [LabeledPrice(label="6 month", amount=7000)]
        }
    else:
        logging.error('Cannot parse method (pts/month_sub)', method)
        return

    try:
        amount = int(amount)
    except ValueError:
        logging.error('Cannot parse amount %s', callback.data.split()[1])
        return

    await callback.bot.send_invoice(
        chat_id=callback.from_user.id,
        title='IELTS Exam Bot: Your Personal Assistant for IELTS Preparation',
        description='Effective IELTS preparation with personalized exercises, expert tips, and a motivation system.',
        payload=json.dumps({
            'user_id': callback.from_user.id,
            'method': method,
            'amount': amount,
            'price': price[amount][0].amount
        }),
        currency='XTR',
        prices=price[amount]
    )

    user = await tg_user_service.get_or_create_tg_user(callback.from_user.id)
    await tg_user_service.adapter.analytics_client.send_event(
        str(uuid.uuid4()),
        umt_data_dict=user.utm_data_json,
        event_name='conversion_event_begin_checkout',
    )


@router.pre_checkout_query()
async def precheckout_callback(pre_checkout_query: types.PreCheckoutQuery):
    if pre_checkout_query.total_amount:
        await pre_checkout_query.bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@router.message(
    F.successful_payment,
    INJECTOR.inject_tg_user,
    INJECTOR.inject_subscription
)
async def successful_payment_handler(
    message: types.Message,
    state: FSMContext,
    tg_user_service: TgUserService,
    subscription_service: SubscriptionService
):
    successful_payment = message.successful_payment
    if not successful_payment:
        return

    invoice_payload = json.loads(successful_payment.invoice_payload)
    user_id_from_payload = invoice_payload['user_id']
    method = invoice_payload['method']
    purchased_amount = invoice_payload['amount']
    price = invoice_payload['price']

    if user_id_from_payload == message.from_user.id:
        if method == 'pts':
            user_instance = await tg_user_service.add_points(user_id_from_payload, purchased_amount)
        elif method == 'month_sub':
            user_instance = await tg_user_service.get_or_create_tg_user(user_id_from_payload)
            await subscription_service.add_subscription(user_instance.id, purchased_amount)
        else:
            logging.error(f'Cannot parse method (pts/month_sub) {method}')
            return
        if user_instance:
            await tg_user_service.mark_user_activity(message.from_user.id, f'buy {method}')
            await tg_user_service.mark_user_balance(message.from_user.id, 'Telegram', price, 'TGS')
            if method == 'pts':
                await tg_user_service.mark_user_pts(message.from_user.id, 'buy', purchased_amount)

            await tg_user_service.adapter.analytics_client.send_event(
                str(uuid.uuid4()),
                event_name='conversion_event_purchase',
                umt_data_dict=user_instance.utm_data_json
            )
    else:
        logging.critical(f'Payment failed for user {message.from_user.id} (from payload - {user_id_from_payload}) '
                         f'(user_id_from_payload != message.from_user.id)')

    await message.answer("Thank you for your purchase! Your payment was successful.")

    state_data = await state.get_data()
    logging.info(state_data)
    task_ready_to_proceed = state_data.get('task_ready_to_proceed', None)
    logging.info(task_ready_to_proceed)
    if task_ready_to_proceed is not None:
        text = ('Thank you for completing all the questions! To confirm your response, '
                'please click "Continue"')
        builder = InlineKeyboardBuilder([
            [InlineKeyboardButton(text='Continue', callback_data=f'confirm_task_{task_ready_to_proceed} premium')],
        ])
        await message.answer(text, reply_markup=builder.as_markup())
    else:
        await answer_menu(message)
