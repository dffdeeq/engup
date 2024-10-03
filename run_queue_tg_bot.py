import asyncio
import logging

from src.libs.adapter import Adapter
from src.postgres.factory import initialize_postgres_pool
from src.postgres.models.temp_data import TempData
from src.postgres.models.tg_user_question import TgUserQuestion
from src.rabbitmq.worker.factories.tgbot_worker import TgBotWorker
from src.repos.factories.temp_data import TempDataRepo
from src.repos.factories.user_question import TgUserQuestionRepo
from src.services.factories.status_service import StatusService
from src.settings import Settings

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


async def main():
    settings = Settings.new()
    session = initialize_postgres_pool(settings.postgres)

    status_service = StatusService(
        TgUserQuestionRepo(TgUserQuestion, session),
        Adapter(
            settings
        ),
        session,
        settings
    )

    tg_bot_worker = TgBotWorker(
        repo=TempDataRepo(TempData, session),
        dsn_string=settings.rabbitmq.dsn,
        settings=settings,
        queue_name='tg_bot',
        session=session,
        status_service=status_service
    )

    tg_bot_sender = TgBotWorker(
        repo=TempDataRepo(TempData, session),
        dsn_string=settings.rabbitmq.dsn,
        settings=settings,
        queue_name='tg_bot_sender',
        session=session,
        status_service=status_service
    )

    tg_bot_mailing = TgBotWorker(
        repo=TempDataRepo(TempData, session),
        dsn_string=settings.rabbitmq.dsn,
        settings=settings,
        queue_name='tg_bot_mailing',
        session=session,
        status_service=status_service
    )

    await asyncio.gather(
        tg_bot_worker.start_listening(
            'tg_bot_return_simple_result_to_user', tg_bot_worker.process_return_simple_result_task,
        ),
        tg_bot_sender.start_listening(
            'log_error_into_support_group', tg_bot_sender.log_error_into_support_group,
        ),
    )


if __name__ == '__main__':
    asyncio.run(main())
