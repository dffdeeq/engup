import logging
import typing as T  # noqa
from collections import defaultdict

from aio_pika.abc import AbstractRobustConnection
from sqlalchemy import update, and_, select
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.postgres.models.temp_data import TempData
from src.postgres.models.tg_user_question import TgUserQuestion
from src.rabbitmq.producer.factories.gpt import GPTProducer
from src.rabbitmq.worker.factory import RabbitMQWorkerFactory
from src.repos.factories.temp_data import TempDataRepo
from src.services.factories.apihost import ApiHostService


class ApiHostWorker(RabbitMQWorkerFactory):
    def __init__(
        self,
        session: async_sessionmaker,
        repo: TempDataRepo,
        connection_pool: AbstractRobustConnection,
        queues_info: T.List[T.Tuple[str, str]],
        apihost_service: ApiHostService,
        gpt_producer: GPTProducer,
    ):
        super().__init__(repo, connection_pool, queues_info)
        self.session = session
        self.repo = repo
        self.apihost_service = apihost_service
        self.gpt_producer = gpt_producer

    async def process_answers(self, updates: T.Dict[str, T.Any]):
        logging.info(f'---------- Start of Task {self.process_answers.__name__} ----------')
        uq_id = await self.update_multiple_temp_data_answers(updates['filenames'])
        if uq_id:
            logging.info('apihost --> update_multiple_temp_data_answers == OK')
            all_user_qa = await self.get_all_user_qa(uq_id)
            async with self.session() as session:
                premium_queue = (await session.execute(
                    update(TgUserQuestion)
                    .where(and_(TgUserQuestion.id == uq_id))
                    .values(user_answer_json=all_user_qa, status=True)
                    .returning(TgUserQuestion.premium_queue)
                )).scalar_one_or_none()
                await session.commit()
                logging.info('apihost --> update_user_answer_json == OK')
            logging.info('apihost --> gpt (create_task_generate_result) == OK')
            await self.gpt_producer.create_task_generate_result(uq_id, premium_queue=premium_queue)
        logging.info(f'---------- End of Task {self.process_answers.__name__} ----------')

    async def update_multiple_temp_data_answers(self, updates: T.List[T.Dict[str, str]]) -> T.Optional[int]:
        async with self.session() as session:
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

    async def send_files_to_transcription_and_clear(self, filepaths: T.Dict[str, T.List[str]]) -> None:
        await self.apihost_service.send_to_transcription(filepaths['files'])
