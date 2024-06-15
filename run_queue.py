import asyncio
import logging

import aio_pika

from src.libs.adapter import Adapter
from src.libs.factories.gpt.models.competence import Competence
from src.postgres.factory import initialize_postgres_pool
from src.postgres.models.question import Question
from src.rabbitmq.consumer.factories.gpt_service_worker import GPTWorker
from src.repos.factories.question import QuestionRepo
from src.services.factories.gpt import GPTService
from src.settings import Settings

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


async def main():
    settings = Settings.new()
    connection_pool = await aio_pika.connect_robust(url=settings.rabbitmq.dsn)
    session = initialize_postgres_pool(settings.postgres)
    gpt_worker = GPTWorker(
        connection_pool=connection_pool,
        session=session,
        gpt_service=GPTService(
            repo=QuestionRepo(Question, session),
            adapter=Adapter(settings),
            session=session,
            settings=settings
        ),
        queue_name='gpt_service',
        routing_key='text_to_result'
    )
    await gpt_worker.start_listening(gpt_worker.send_text_to_get_result, Competence.writing)


if __name__ == '__main__':
    asyncio.run(main())
