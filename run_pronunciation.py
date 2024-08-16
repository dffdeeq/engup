import asyncio
import logging

from src.libs.factories.gpt import GPTClient
from src.libs.http_client import HttpClient
from src.postgres.factory import initialize_postgres_pool
from src.postgres.models.tg_user_question import TgUserQuestionMetric
from src.rabbitmq.worker.factories.pronunciation_worker import PronunciationWorker
from src.repos.factories.user_question_metric import TgUserQuestionMetricRepo
from src.settings import Settings

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


async def main():
    settings = Settings.new()
    session = initialize_postgres_pool(settings.postgres)
    pronunciation_worker = PronunciationWorker(
        session,
        TgUserQuestionMetricRepo(TgUserQuestionMetric, session),
        dsn_string=settings.rabbitmq.dsn,
        queue_name='pronunciation',
        gpt_client=GPTClient(
            HttpClient(),
            settings.gpt
        )
    )
    await pronunciation_worker.start_listening(
        'pronunciation_score_generate', pronunciation_worker.get_pronuncation)


if __name__ == '__main__':
    asyncio.run(main())
