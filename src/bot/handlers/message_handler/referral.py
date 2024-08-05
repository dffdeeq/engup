from aiogram import Router, F, types
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.bot.injector import INJECTOR
from src.services.factories.tg_user import TgUserService

router = Router(name=__name__)


@router.callback_query(F.data == 'referral', INJECTOR.inject_tg_user)
async def referral_callback(callback: types.CallbackQuery, tg_user_service: TgUserService):
    user = await tg_user_service.get_or_create_tg_user(callback.from_user.id)
    user_referrals_count = await tg_user_service.get_user_referrals(callback.from_user.id, count_only=True)

    bot_username = (await callback.bot.get_me()).username
    start_link = f'https://t.me/{bot_username}?start={user.id}'
    text = (f'You have {user_referrals_count} referrals.\n'
            f'When a referral passes three tests, you will receive 5 free premium tests\n\n'
            f'Your link (Copies when clicked):\n<code>{start_link}</code>')

    builder = InlineKeyboardBuilder([
        [InlineKeyboardButton(text='Share link', switch_inline_query=start_link)],
        [InlineKeyboardButton(text='🔙 Back', callback_data='free_tests'), ],
    ])

    await callback.message.edit_text(text=text, reply_markup=builder.as_markup())
