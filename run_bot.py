import asyncio
import logging

from aiogram import Bot
from aiogram.types import BotCommand

from src.bot.core.bot import get_bot
from src.bot.core.dispatcher import get_dispatcher
from src.bot.handlers import register_handlers
from src.bot.injector import INJECTOR


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="/menu", description="Menu"),
    ]
    await bot.set_my_commands(commands)


async def main():
    bot = get_bot(INJECTOR.settings)
    await bot.delete_webhook()
    dp = get_dispatcher()

    register_handlers(dp)

    await set_commands(bot)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
