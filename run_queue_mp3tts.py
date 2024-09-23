import asyncio
import logging

from src.libs.adapter import Adapter
from src.postgres.factory import initialize_postgres_pool
from src.postgres.models.temp_data import TempData
from src.postgres.models.tg_user import TgUser
from src.postgres.models.tg_user_activity import TgUserActivity
from src.postgres.models.tg_user_question import TgUserQuestion
from src.rabbitmq.worker.factories.mp3tts_service_worker import MP3TTSWorker
from src.repos.factories.activity import ActivityRepo
from src.repos.factories.temp_data import TempDataRepo
from src.repos.factories.user import TgUserRepo
from src.repos.factories.user_question import TgUserQuestionRepo
from src.services.factories.mp3tts import MP3TTSService
from src.services.factories.status_service import StatusService
from src.services.factories.tg_user import TgUserService
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

    user_service = TgUserService(
        TgUserRepo(TgUser, session),
        ActivityRepo(TgUserActivity, session),
        adapter,
        session,
        settings
    )

    mp3tts_transcription_worker = MP3TTSWorker(
        repo=TempDataRepo(TempData, session),
        session=session,
        dsn_string=settings.rabbitmq.dsn,
        queue_name='apihost_transcription',
        mp3tts_service=MP3TTSService(
            repo=TgUserRepo(TgUser, session),
            adapter=adapter,
            session=session,
            settings=settings
        ),
        status_service=status_service,
        user_service=user_service,
        settings=settings
    )
    mp3tts_process_answers_worker = MP3TTSWorker(
        repo=TempDataRepo(TempData, session),
        session=session,
        dsn_string=settings.rabbitmq.dsn,
        queue_name='apihost_process_answers',
        mp3tts_service=MP3TTSService(
            repo=TgUserRepo(TgUser, session),
            adapter=adapter,
            session=session,
            settings=settings
        ),
        status_service=status_service,
        user_service=user_service,
        settings=settings
    )
    await asyncio.gather(
        mp3tts_transcription_worker.start_listening(
            'apihost_to_transcription', mp3tts_transcription_worker.send_files_to_transcription),
        mp3tts_process_answers_worker.start_listening(
            'apihost_update_answers', mp3tts_process_answers_worker.process_answers)
    )


if __name__ == '__main__':
    asyncio.run(main())
