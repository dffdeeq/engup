from aiogram.filters import Filter
from aiogram.types import Message

from src.bot.handlers.constants import SpeakingMessages


class VoicemailFilter(Filter):
    """
    A filter to check if a message contains a voicemail.
    """
    async def __call__(self, message: Message) -> bool:
        if message.voice is None:
            await message.answer(SpeakingMessages.COULDNT_FIND_AUDIO)
            return False
        else:
            return True
