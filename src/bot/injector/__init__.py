from src.bot.injector.base import BaseInjector
from src.bot.injector.factories.apihost_client_injector import ApiHostClientInjectorMixin
from src.bot.injector.factories.gpt_service_injector import GPTServiceInjectorMixin
from src.bot.injector.factories.tg_bot_service_injector import TgBotServiceInjectorMixin
from src.settings import Settings


class _I(
    ApiHostClientInjectorMixin,
    GPTServiceInjectorMixin,
    TgBotServiceInjectorMixin,
    BaseInjector
):
    def __init__(self, settings: Settings):
        super().__init__(settings)


INJECTOR: _I = _I(Settings.new())
