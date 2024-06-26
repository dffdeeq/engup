import asyncio
import logging

import aio_pika

from src.postgres.factory import initialize_postgres_pool
from src.postgres.models.temp_data import TempData
from src.rabbitmq.worker.factories.tgbot_worker import TgBotWorker
from src.repos.factories.temp_data import TempDataRepo
from src.settings import Settings

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


async def main():
    settings = Settings.new()
    connection_pool = await aio_pika.connect_robust(url=settings.rabbitmq.dsn)
    session = initialize_postgres_pool(settings.postgres)
    tg_bot_worker = TgBotWorker(
        repo=TempDataRepo(TempData, session),
        connection_pool=connection_pool,
        session=session,
        queues_info=[
            ('tgbot', 'tg_bot_return_result_to_user'),
            ('tgbot', 'tg_bot_return_simple_result_to_user'),
        ],
    )
    await tg_bot_worker.start_listening({
        'tg_bot_return_result_to_user': tg_bot_worker.process_return_result_task,
        'tg_bot_return_simple_result_to_user': tg_bot_worker.process_return_simple_result_task,
    })


if __name__ == '__main__':
    asyncio.run(main())
