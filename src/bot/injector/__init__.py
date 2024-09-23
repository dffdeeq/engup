from src.bot.injector.base import BaseInjector
from src.bot.injector.factories.answer_process_injector import AnswerProcessInjectorMixin
from src.bot.injector.factories.mp3tts_client_injector import MP3TTSClientInjectorMixin
from src.bot.injector.factories.apihost_producer_injector import ApiHostProducerInjectorMixin
from src.bot.injector.factories.feedback_service_injector import FeedbackInjectorMixin
from src.bot.injector.factories.gpt_producer_injector import GPTProducerInjectorMixin
from src.bot.injector.factories.question_service_injector import QuestionServiceInjectorMixin
from src.bot.injector.factories.status_service_injector import StatusServiceInjectorMixin
from src.bot.injector.factories.subscription_service_injector import SubscriptionServiceInjectorMixin
from src.bot.injector.factories.tg_user_service_injector import TgUserServiceInjectorMixin
from src.bot.injector.factories.user_question_service_injector import UserQuestionServiceInjectorMixin
from src.bot.injector.factories.voice_service_injector import VoiceServiceInjectorMixin
from src.bot.injector.factories.metrics_service_injector import MetricsServiceInjectorMixin
from src.bot.injector.factories.s3_injector import S3InjectorMixin
from src.settings import Settings


class _I(
    MP3TTSClientInjectorMixin,
    TgUserServiceInjectorMixin,
    VoiceServiceInjectorMixin,
    ApiHostProducerInjectorMixin,
    QuestionServiceInjectorMixin,
    UserQuestionServiceInjectorMixin,
    AnswerProcessInjectorMixin,
    GPTProducerInjectorMixin,
    StatusServiceInjectorMixin,
    FeedbackInjectorMixin,
    MetricsServiceInjectorMixin,
    S3InjectorMixin,
    SubscriptionServiceInjectorMixin,
    BaseInjector
):
    def __init__(self, settings: Settings):
        super().__init__(settings)


INJECTOR: _I = _I(Settings.new())
