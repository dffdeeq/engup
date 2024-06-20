import asyncio
import logging

import aio_pika

from src.libs.adapter import Adapter
from src.postgres.factory import initialize_postgres_pool
from src.postgres.models.question import Question
from src.postgres.models.temp_data import TempData
from src.rabbitmq.producer.factories.gpt import GPTProducer
from src.rabbitmq.worker.factories.gpt_service_worker import GPTWorker
from src.repos.factories.question import QuestionRepo
from src.repos.factories.temp_data import TempDataRepo
from src.services.factories.result import ResultService
from src.settings import Settings

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


async def main():
    settings = Settings.new()
    connection_pool = await aio_pika.connect_robust(url=settings.rabbitmq.dsn)
    session = initialize_postgres_pool(settings.postgres)
    adapter = Adapter(settings)
    gpt_worker = GPTWorker(
        repo=TempDataRepo(TempData, session),
        connection_pool=connection_pool,
        session=session,
        queues_info=[
            ('gpt', 'gpt_generate_result'),
        ],
        result_service=ResultService(
            repo=QuestionRepo(Question, session),
            adapter=adapter,
            session=session,
            settings=settings
        ),
        gpt_producer=GPTProducer(
            dsn_string=settings.rabbitmq.dsn,
            adapter=adapter,
        ),
    )
    await gpt_worker.start_listening({
        'gpt_generate_result': gpt_worker.process_result_task,
    })


if __name__ == '__main__':
    asyncio.run(main())
