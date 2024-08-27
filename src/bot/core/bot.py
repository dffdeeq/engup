from aiogram import Bot
from aiogram.client.default import DefaultBotProperties

from src.settings import Settings


def get_bot(settings: Settings) -> Bot:
    return Bot(token=settings.bot.bot_token, default=DefaultBotProperties(parse_mode='HTML'))
