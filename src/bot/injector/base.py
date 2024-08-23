from src.libs.adapter import Adapter
from src.libs.factories.apihost import ApiHostClient
from src.libs.http_client import HttpClient
from src.postgres.factory import initialize_postgres_pool
from src.postgres.models.poll_feedback import PollFeedback
from src.postgres.models.question import Question
from src.postgres.models.temp_data import TempData
from src.postgres.models.tg_user import TgUser
from src.postgres.models.tg_user_activity import TgUserActivity
from src.postgres.models.tg_user_question import TgUserQuestion
from src.rabbitmq.producer.factories.apihost import ApiHostProducer
from src.rabbitmq.producer.factories.gpt import GPTProducer
from src.repos.factories.activity import ActivityRepo
from src.repos.factories.feedback import FeedbackRepo
from src.repos.factories.question import QuestionRepo
from src.repos.factories.temp_data import TempDataRepo
from src.repos.factories.user import TgUserRepo
from src.repos.factories.user_question import TgUserQuestionRepo
from src.services.factories.S3 import S3Service
from src.services.factories.answer_process import AnswerProcessService
from src.services.factories.feedback import FeedbackService
from src.services.factories.question import QuestionService
from src.services.factories.status_service import StatusService
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
        tg_user_repo = TgUserRepo(TgUser, self.session)
        tg_user_question_repo = TgUserQuestionRepo(TgUserQuestion, self.session)

        self.question_service = QuestionService(
            repo=QuestionRepo(Question, self.session),
            adapter=self.adapter,
            session=self.session,
            settings=self.settings
        )
        self.uq_service = UserQuestionService(
            repo=tg_user_question_repo,
            adapter=self.adapter,
            session=self.session,
            settings=self.settings,
            user_repo=tg_user_repo
        )
        self.tg_user_service = TgUserService(
            repo=tg_user_repo,
            activity_repo=ActivityRepo(TgUserActivity, self.session),
            adapter=self.adapter,
            session=self.session,
            settings=self.settings,
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
        self.gpt_producer = GPTProducer(
            dsn_string=settings.rabbitmq.dsn,
            exchange_name='direct',
            adapter=self.adapter
        )
        self.answer_process = AnswerProcessService(
            repo=TempDataRepo(TempData, self.session),
            adapter=self.adapter,
            session=self.session,
            settings=self.settings,
            user_qa_repo=tg_user_question_repo
        )
        self.status_service = StatusService(
            user_qa_repo=tg_user_question_repo,
            adapter=self.adapter,
            session=self.session,
            settings=self.settings,
        )
        self.feedback_service = FeedbackService(
            FeedbackRepo(
                PollFeedback,
                self.session
            ),
            self.adapter,
            self.session,
            self.settings
        )
        self.s3 = S3Service(
            repo=TempDataRepo(
                TempData,
                self.session
            ),
            adapter=Adapter(
                settings=settings,
            ),
            session=self.session,
            settings=settings
        )
