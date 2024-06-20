import asyncio
import logging

import aio_pika

from src.libs.adapter import Adapter
from src.postgres.factory import initialize_postgres_pool
from src.postgres.models.temp_data import TempData
from src.postgres.models.tg_user import TgUser
from src.rabbitmq.producer.factories.gpt import GPTProducer
from src.rabbitmq.worker.factories.apihost_service_worker import ApiHostWorker
from src.repos.factories.temp_data import TempDataRepo
from src.repos.factories.user import TgUserRepo
from src.services.factories.apihost import ApiHostService
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
    apihost_worker = ApiHostWorker(
        repo=TempDataRepo(TempData, session),
        connection_pool=connection_pool,
        session=session,
        apihost_service=ApiHostService(
            repo=TgUserRepo(TgUser, session),
            adapter=adapter,
            session=session,
            settings=settings
        ),
        queues_info=[
            ('apihost', 'apihost_to_transcription'),
            ('apihost', 'apihost_update_answers')
        ],
        gpt_producer=GPTProducer(
            dsn_string=settings.rabbitmq.dsn,
            adapter=adapter
        ),
    )
    await apihost_worker.start_listening({
        'apihost_to_transcription': apihost_worker.send_files_to_transcription_and_clear,
        'apihost_update_answers': apihost_worker.process_answers
    })


if __name__ == '__main__':
    asyncio.run(main())
