import logging
import typing as T  # noqa

from aio_pika.abc import AbstractRobustConnection
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.libs.factories.gpt.models.result import Result
from src.postgres.enums import CompetenceEnum
from src.postgres.models.question import Question
from src.postgres.models.tg_user import TgUser
from src.postgres.models.tg_user_question import TgUserQuestion
from src.rabbitmq.producer.factories.gpt import GPTProducer
from src.rabbitmq.worker.factory import RabbitMQWorkerFactory
from src.repos.factories.temp_data import TempDataRepo
from src.services.factories.result import ResultService


class GPTWorker(RabbitMQWorkerFactory):
    def __init__(
        self,
        session: async_sessionmaker,
        repo: TempDataRepo,
        connection_pool: AbstractRobustConnection,
        queues_info: T.List[T.Tuple[str, str]],
        result_service: ResultService,
        gpt_producer: GPTProducer,
    ):
        super().__init__(repo, connection_pool, queues_info)
        self.repo = repo
        self.session = session
        self.result_service = result_service
        self.gpt_producer = gpt_producer

    async def process_result_task(self, uq_id: T.Dict[str, int]):
        logging.info(f'---------- Start of Task {self.process_result_task.__name__} ----------')
        async with self.session() as session:
            query = await session.execute(
                select(TgUserQuestion, TgUser.id, Question.competence)
                .join(Question, TgUserQuestion.question_id == Question.id)
                .join(TgUser, TgUserQuestion.user_id == TgUser.id)
                .where(and_(TgUserQuestion.id == uq_id['uq_id'])))
            instance, user_id, competence = query.first()
            request_text = await self.format_user_qa_to_text(instance)
            result = await self.get_result(request_text, competence)
            if result:
                instance.user_result_json = result.model_dump()
                await self.gpt_producer.create_task_return_result_to_user(user_id, result)

        logging.info(f'---------- End of Task {self.process_result_task.__name__} ----------')

    @staticmethod
    async def format_user_qa_to_text(uq_instance: TgUserQuestion) -> str:
        parts_text = []
        for part, questions in uq_instance.user_answer_json.items():
            part_num = part.split('_')[1]
            part_text = [f"Part {part_num}:\n"]
            for i, q in enumerate(questions):
                part_text.append(f"Q: {q['card_text']}\nA: {q['user_answer']}\n")
            parts_text.append("".join(part_text))
        return "\n".join(parts_text)

    async def get_result(self, qa_string: str, competence: CompetenceEnum) -> Result:
        try:
            result = await self.result_service.generate_result(qa_string, competence)
            if result:
                return result
        except Exception as e:
            logging.error(e)
