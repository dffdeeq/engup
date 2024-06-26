from aiogram.filters import Filter
from aiogram.types import Message

from src.bot.handlers.constants import DefaultMessages
from src.bot.handlers.utils import is_english, is_copypaste


class EssayFilter(Filter):
    """
    A filter to check if a message contains a valid english essay.
    """
    async def __call__(self, message: Message) -> bool:
        if len(message.text.split()) < 150:
            warning = DefaultMessages.TOO_SHORT_TEXT_WARNING
        elif not is_english(message.text):
            warning = DefaultMessages.TEXT_IS_NOT_ENGLISH
        elif is_copypaste(message.text):
            warning = DefaultMessages.TEXT_IS_COPY_PASTE
        else:
            return True

        await message.answer(text=warning)
        return False
