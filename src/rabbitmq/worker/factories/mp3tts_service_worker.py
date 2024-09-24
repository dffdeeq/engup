import asyncio
import logging
import os.path
import typing as T  # noqa
from collections import defaultdict

import fal_client
from sqlalchemy import update, and_, select
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.postgres.models.temp_data import TempData
from src.postgres.models.tg_user import TgUser
from src.postgres.models.tg_user_question import TgUserQuestion
from src.rabbitmq.worker.enums import ErrorTypeEnum
from src.rabbitmq.worker.factory import RabbitMQWorkerFactory
from src.repos.factories.temp_data import TempDataRepo
from src.services.constants import TextTemplates
from src.services.factories.mp3tts import MP3TTSService
from src.services.factories.status_service import StatusService
from src.services.factories.tg_user import TgUserService
from src.settings import Settings
from src.settings.static import TEMP_FILES_DIR


class MP3TTSWorker(RabbitMQWorkerFactory):
    def __init__(
        self,
        session: async_sessionmaker,
        repo: TempDataRepo,
        dsn_string: str,
        settings: Settings,
        queue_name: str,
        mp3tts_service: MP3TTSService,
        status_service: StatusService,
        user_service: TgUserService
    ):
        super().__init__(repo, dsn_string, queue_name)
        self.session = session
        self.repo = repo
        self.settings = settings
        self.mp3tts_service = mp3tts_service
        self.status_service = status_service
        self.user_service = user_service

        os.environ["FAL_KEY"] = self.settings.nn_models.fal_key
        self.fal_client = fal_client

    async def process_answers(self, updates: T.Dict[str, T.Any]):
        logging.info(f'---------- Start of Task {self.process_answers.__name__} ----------')
        uq_id = await self.update_multiple_temp_data_answers(updates['file_names'])
        if uq_id is None:
            return

        await self.update_user_qa_and_send_to_gpt(uq_id)

    async def update_user_qa_and_send_to_gpt(self, uq_id: int):
        await self.status_service.change_qa_status(uq_id, 'Processing transcription.')
        logging.info('apihost --> update_multiple_temp_data_answers == OK')
        all_user_qa = await self.get_all_user_qa(uq_id)
        async with self.session() as session:
            premium_queue = (await session.execute(
                update(TgUserQuestion)
                .where(and_(TgUserQuestion.id == uq_id))
                .values(user_answer_json=all_user_qa, status=True, current_result_status='Processing transcription')
                .returning(TgUserQuestion.premium_queue)
            )).scalar_one_or_none()
            await session.commit()
            logging.info('apihost --> update_user_answer_json == OK')
        await self.publish(
            json_serializable_dict={'uq_id': uq_id},
            routing_key='gpt_generate_result_use_local_model',
            priority=self.get_priority(premium_queue)
        )
        logging.info('apihost --> gpt (create_task_generate_result) == OK')
        logging.info(f'---------- End of Task {self.process_answers.__name__} ----------')

    async def update_multiple_temp_data_answers(self, updates: T.List[T.Dict[str, str]]) -> T.Optional[int]:
        async with self.session() as session:
            non_existent_filenames = await self.get_non_existent_temp_data([i['name'] for i in updates])
            if not non_existent_filenames:
                return None

            async with session.begin():
                for update_data in updates:
                    filename = update_data['name']
                    new_text = update_data['text']
                    result = await session.execute(
                        update(TempData)
                        .where(and_(TempData.filename == filename))
                        .values(answer_text=new_text)
                        .returning(TempData.tg_user_question_id)
                    )
                await session.commit()
                return result.scalars().first()

    async def get_non_existent_temp_data(self, filenames) -> T.Optional[T.List]:
        async with self.session() as session:
            already_exists_query = select(TempData.filename).where(
                and_(TempData.answer_text.is_(None), TempData.filename.in_(filenames))
            )
            result = await session.execute(already_exists_query)
            return list(result.scalars().all())

    async def get_all_user_qa(self, uq_id: int):
        async with self.session() as session:
            result = await session.execute(select(TempData).where(and_(TempData.tg_user_question_id == uq_id)))
            temp_data_objects = result.scalars().all()
            collected_data = defaultdict(list)
            for temp_data in temp_data_objects:
                part_key = f'part_{temp_data.part.value}'
                collected_data[part_key].append({
                    'card_text': temp_data.question_text,
                    'user_answer': temp_data.answer_text
                })
            return collected_data

    async def send_files_to_transcription(self, data: T.Dict[str, T.Any]) -> None:
        user_obj = await self.user_service.get_tg_user_by_uq_id(data['uq_id'])
        filenames = [os.path.basename(file) for file in data['file_names']]
        timeout = 5 * 60
        message = TextTemplates.MP3TTS_TIMEOUT_ERROR.format(timeout=timeout)

        if not await self.get_non_existent_temp_data(filenames):
            logging.info('temp data already updated, skipping...')
            return

        try:
            if not self.mp3tts_service.settings.mp3tts.debug_mode:
                result = await self.mp3tts_service.send_to_transcription(data['file_names'])
                if result is None:
                    raise Exception(message)
        except Exception as e:
            logging.error(e)
            await self.fal_ai_process_transcription(filenames, data['uq_id'], user_obj, str(e))
            return

        logging.info(f'waiting mp3tts for {timeout} seconds...')
        await asyncio.sleep(timeout)
        await self.fal_ai_process_transcription(filenames, data['uq_id'], user_obj, message)

    async def fal_ai_process_transcription(
        self,
        filenames: T.List[str],
        uq_id: int,
        user_obj: TgUser,
        error_text: str = ''
    ) -> None:
        if non_existent_filenames := await self.get_non_existent_temp_data(filenames):
            logging.info('temp data is not yet updated')
            await self.log_error_into_support_group(uq_id, user_obj, ErrorTypeEnum.mp3tts, error_text)

            non_existent_filepaths = [str(os.path.join(TEMP_FILES_DIR, f)) for f in non_existent_filenames]
            try:
                await self.transcribe_files(non_existent_filepaths)
            except Exception as e:
                await self.log_error_into_support_group(uq_id, user_obj, ErrorTypeEnum.fal_ai, str(e))

        logging.info('temp data updated')

    async def transcribe_files(self, filepaths: T.List[str]):
        urls = await self.fal_ai_upload_files_and_get_urls(filepaths)
        for url in urls:
            url['text'] = await self.fal_ai_transcribe_file(url['url'])
        uq_id = await self.update_multiple_temp_data_answers(urls)
        await self.update_user_qa_and_send_to_gpt(uq_id)

    async def fal_ai_transcribe_file(self, audio_url: str) -> T.Optional[str]:
        handler = await self.fal_client.submit_async(
            "fal-ai/wizper",
            arguments={
                "audio_url": audio_url,
                "task": "transcribe",
                "language": "en",
                "chunk_level": "segment",
                "version": "3"
            },
        )

        log_index = 0
        async for event in handler.iter_events(with_logs=False):
            try:
                if isinstance(event, fal_client.InProgress):
                    new_logs = event.logs[log_index:]
                    for log in new_logs:
                        print(log['message'])
                    log_index = len(event.logs)
            except Exception as e:
                logging.error(e)
                break

        result = await handler.get()
        text = result.get('text')
        return text

    async def fal_ai_upload_files_and_get_urls(self, filepaths: T.List[str]) -> T.List[T.Dict[str, str]]:
        urls = []
        for filepath in filepaths:
            url = await self.fal_client.upload_file_async(filepath)
            urls.append({'name': os.path.basename(filepath), 'url': url})
        return urls

    async def log_error_into_support_group(
        self,
        uq_id: int,
        user_obj: TgUser,
        error_type: ErrorTypeEnum,
        error_text: str
    ):
        if error_type == ErrorTypeEnum.mp3tts:
            text = 'Mp3tts service error'
        elif error_type == ErrorTypeEnum.fal_ai:
            text = 'The transcription generation by the fal.ai service has failed. A retry will start in 1 hour.'
        else:
            text = 'Undescribed error'

        text += f'\n\nuser_id: {user_obj.id}\n@{user_obj.username}\nuq_id: {uq_id}\n\n<code>{error_text}</code>'

        data = {'error_text': text}
        await self.publish(data, 'log_error_into_support_group')
