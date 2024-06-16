import asyncio
import logging

import aio_pika

from src.libs.adapter import Adapter
from src.postgres.factory import initialize_postgres_pool
from src.postgres.models.tg_user import TgUser
from src.rabbitmq.consumer.factories.apihost_service_worker import ApiHostWorker
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
    apihost_worker = ApiHostWorker(
        connection_pool=connection_pool,
        session=session,
        apihost_service=ApiHostService(
            repo=TgUserRepo(TgUser, session),
            adapter=Adapter(settings),
            session=session,
            settings=settings
        ),
        queue_name='apihost',
        routing_key='to_transcription'
    )
    await apihost_worker.start_listening(apihost_worker.send_text_to_get_result_handle)


if __name__ == '__main__':
    asyncio.run(main())
