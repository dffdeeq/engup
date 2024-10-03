from src.libs.adapter import Adapter
from src.postgres.factory import initialize_postgres_pool
from src.postgres.models.metrics_data import MetricsData
from src.postgres.models.question import Question
from src.postgres.models.temp_data import TempData
from src.postgres.models.tg_user import TgUser
from src.postgres.models.tg_user_activity import TgUserActivity
from src.postgres.models.tg_user_question import TgUserQuestion
from src.rabbitmq.producer.factories.mp3tts import MP3TTSProducer
from src.repos.factories.activity import ActivityRepo
from src.repos.factories.metrics_data import MetricsDataRepo
from src.repos.factories.question import QuestionRepo
from src.repos.factories.temp_data import TempDataRepo
from src.repos.factories.user import TgUserRepo
from src.repos.factories.user_question import TgUserQuestionRepo
from src.services.factories.S3 import S3Service
from src.services.factories.question import QuestionService
from src.services.factories.user_question import UserQuestionService
from src.settings import Settings

settings = Settings.new()
adapter = Adapter(settings)
session = initialize_postgres_pool(settings.postgres)


async def get_apihost_producer() -> MP3TTSProducer:
    return MP3TTSProducer(
        dsn_string=settings.rabbitmq.dsn,
        adapter=adapter
    )


async def get_metrics_repo() -> MetricsDataRepo:
    return MetricsDataRepo(
        model=MetricsData,
        session=session
    )


async def get_question_service() -> QuestionService:
    return QuestionService(
        S3Service(
            TempDataRepo(TempData, session),
            adapter,
            session,
            settings,
        ),
        QuestionRepo(Question, session),
        adapter,
        session,
        settings
    )


async def get_user_question_service() -> UserQuestionService:
    return UserQuestionService(
        TgUserQuestionRepo(TgUserQuestion, session),
        adapter,
        session,
        settings,
        TgUserRepo(TgUser, session),
        ActivityRepo(TgUserActivity, session)
    )
