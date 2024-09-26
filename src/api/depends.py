from src.libs.adapter import Adapter
from src.postgres.factory import initialize_postgres_pool
from src.postgres.models.metrics_data import MetricsData
from src.postgres.models.question import Question
from src.postgres.models.temp_data import TempData
from src.rabbitmq.producer.factories.mp3tts import MP3TTSProducer
from src.repos.factories.metrics_data import MetricsDataRepo
from src.repos.factories.question import QuestionRepo
from src.repos.factories.temp_data import TempDataRepo
from src.services.factories.S3 import S3Service
from src.services.factories.question import QuestionService
from src.settings import Settings

settings = Settings.new()
adapter = Adapter(settings)


async def get_apihost_producer() -> MP3TTSProducer:
    return MP3TTSProducer(
        dsn_string=settings.rabbitmq.dsn,
        adapter=adapter
    )


async def get_metrics_repo() -> MetricsDataRepo:
    session = initialize_postgres_pool(settings.postgres)
    return MetricsDataRepo(
        model=MetricsData,
        session=session
    )


async def get_question_service() -> QuestionService:
    session = initialize_postgres_pool(settings.postgres)
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
