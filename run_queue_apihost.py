import asyncio
import logging

from src.libs.adapter import Adapter
from src.postgres.factory import initialize_postgres_pool
from src.postgres.models.temp_data import TempData
from src.postgres.models.tg_user import TgUser
from src.postgres.models.tg_user_question import TgUserQuestion
from src.rabbitmq.worker.factories.apihost_service_worker import ApiHostWorker
from src.repos.factories.temp_data import TempDataRepo
from src.repos.factories.user import TgUserRepo
from src.repos.factories.user_question import TgUserQuestionRepo
from src.services.factories.apihost import ApiHostService
from src.services.factories.status_service import StatusService
from src.settings import Settings

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


async def main():
    settings = Settings.new()
    session = initialize_postgres_pool(settings.postgres)
    adapter = Adapter(settings)

    status_service = StatusService(
        TgUserQuestionRepo(TgUserQuestion, session),
        adapter,
        session,
        settings
    )

    apihost_transcription_worker = ApiHostWorker(
        repo=TempDataRepo(TempData, session),
        session=session,
        dsn_string=settings.rabbitmq.dsn,
        queue_name='apihost_transcription',
        apihost_service=ApiHostService(
            repo=TgUserRepo(TgUser, session),
            adapter=adapter,
            session=session,
            settings=settings
        ),
        status_service=status_service
    )
    apihost_process_answers_worker = ApiHostWorker(
        repo=TempDataRepo(TempData, session),
        session=session,
        dsn_string=settings.rabbitmq.dsn,
        queue_name='apihost_process_answers',
        apihost_service=ApiHostService(
            repo=TgUserRepo(TgUser, session),
            adapter=adapter,
            session=session,
            settings=settings
        ),
        status_service=status_service
    )
    await asyncio.gather(
        apihost_transcription_worker.start_listening(
            'apihost_to_transcription', apihost_transcription_worker.send_files_to_transcription_and_clear),
        apihost_process_answers_worker.start_listening(
            'apihost_update_answers', apihost_process_answers_worker.process_answers)
    )


if __name__ == '__main__':
    asyncio.run(main())
