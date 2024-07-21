import asyncio
import logging

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
    session = initialize_postgres_pool(settings.postgres)
    tg_bot_worker = TgBotWorker(
        repo=TempDataRepo(TempData, session),
        dsn_string=settings.rabbitmq.dsn,
        queue_name='tg_bot',
        session=session
    )
    await tg_bot_worker.start_listening(
        'tg_bot_return_simple_result_to_user', tg_bot_worker.process_return_simple_result_task)


if __name__ == '__main__':
    asyncio.run(main())
