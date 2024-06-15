from src.bot.injector.base import BaseInjector
from src.bot.injector.factories.apihost_client_injector import ApiHostClientInjectorMixin
from src.bot.injector.factories.apihost_producer import ApiHostProducerInjectorMixin
from src.bot.injector.factories.gpt_service_injector import GPTServiceInjectorMixin
from src.bot.injector.factories.tg_bot_service_injector import TgBotServiceInjectorMixin
from src.bot.injector.factories.voice_service_injector import VoiceServiceInjectorMixin
from src.settings import Settings


class _I(
    ApiHostClientInjectorMixin,
    GPTServiceInjectorMixin,
    TgBotServiceInjectorMixin,
    VoiceServiceInjectorMixin,
    ApiHostProducerInjectorMixin,
    BaseInjector
):
    def __init__(self, settings: Settings):
        super().__init__(settings)


INJECTOR: _I = _I(Settings.new())
