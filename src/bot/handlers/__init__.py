from aiogram import Dispatcher

from .command_handler.menu_command import router as menu_command
from .command_handler.start_command import router as start_command
from .command_handler.dev_command import router as admin_command

from .message_handler.speaking import router as speaking_router
from .message_handler.menu import router as menu_router
from .message_handler.writing import router as writing_router
from .message_handler.pricing import router as pricing_router
from .message_handler.menu_balance import router as menu_balance_router
from .message_handler.dev import router as dev_router
from .message_handler.result_status import router as result_status_router
from .message_handler.menu_ielts import router as menu_ielts_router
from .message_handler.menu_support import router as support_router
from .message_handler.menu_feedback import router as feedback_router
from .message_handler.free_tests import router as free_test_router
from .message_handler.referral import router as referral_router


def register_handlers(dp: Dispatcher):
    dp.include_router(menu_command)
    dp.include_router(start_command)
    dp.include_router(admin_command)

    dp.include_router(speaking_router)
    dp.include_router(menu_router)
    dp.include_router(writing_router)
    dp.include_router(pricing_router)
    dp.include_router(menu_balance_router)
    dp.include_router(dev_router)
    dp.include_router(result_status_router)
    dp.include_router(menu_ielts_router)
    dp.include_router(support_router)
    dp.include_router(feedback_router)
    dp.include_router(referral_router)
    dp.include_router(free_test_router)
