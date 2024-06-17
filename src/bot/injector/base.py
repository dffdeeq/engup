from src.libs.adapter import Adapter
from src.libs.factories.apihost import ApiHostClient
from src.libs.http_client import HttpClient
from src.postgres.factory import initialize_postgres_pool
from src.postgres.models.question import Question
from src.postgres.models.temp_data import TempData
from src.postgres.models.tg_user import TgUser
from src.postgres.models.tg_user_question import TgUserQuestion
from src.rabbitmq.producer.factories.apihost import ApiHostProducer
from src.repos.factories.question import QuestionRepo
from src.repos.factories.temp_data import TempDataRepo
from src.repos.factories.user import TgUserRepo
from src.repos.factories.user_question import TgUserQuestionRepo
from src.services.factories.answer_process import AnswerProcessService
from src.services.factories.question import QuestionService
from src.services.factories.result import ResultService
from src.services.factories.tg_user import TgUserService
from src.services.factories.user_question import UserQuestionService
from src.services.factories.voice import VoiceService
from src.settings import Settings


class BaseInjector:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.session = initialize_postgres_pool(settings.postgres)
        self.http_client = HttpClient()
        self.adapter = Adapter(self.settings)
        self.apihost_client = ApiHostClient(http_client=self.http_client, settings=self.settings.apihost)

        self.question_service = QuestionService(
            repo=QuestionRepo(Question, self.session),
            adapter=self.adapter,
            session=self.session,
            settings=self.settings
        )
        self.result_service = ResultService(
            repo=QuestionRepo(Question, self.session),
            adapter=self.adapter,
            session=self.session,
            settings=self.settings
        )
        self.uq_service = UserQuestionService(
            repo=TgUserQuestionRepo(TgUserQuestion, self.session),
            adapter=self.adapter,
            session=self.session,
            settings=self.settings
        )
        self.tg_user_service = TgUserService(
            repo=TgUserRepo(TgUser, self.session),
            adapter=self.adapter,
            session=self.session,
            settings=self.settings
        )
        self.voice_service = VoiceService(
            repo=QuestionRepo(Question, self.session),
            adapter=self.adapter,
            session=self.session,
            settings=self.settings
        )
        self.apihost_producer = ApiHostProducer(
            dsn_string=settings.rabbitmq.dsn,
            exchange_name='direct',
            adapter=self.adapter
        )
        self.answer_process = AnswerProcessService(
            repo=TempDataRepo(TempData, self.session),
            adapter=self.adapter,
            session=self.session,
            settings=self.settings
        )
