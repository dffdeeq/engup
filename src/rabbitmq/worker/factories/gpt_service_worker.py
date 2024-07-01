import json
import logging
import typing as T  # noqa
from functools import wraps

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
from src.services.factories.user_question import UserQuestionService


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def async_log(func):
    @wraps(func)
    async def wrapper(self, uq_id):
        user_id = uq_id.get('uq_id', 'Unknown user_id')
        logger.info(f"uq_id: {user_id} >>> {func.__name__}")
        result = await func(self, uq_id)
        return result
    return wrapper


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

    async def get_result(self, qa_string: str, competence: CompetenceEnum) -> Result:
        try:
            result = await self.result_service.generate_result(qa_string, competence)
            if result:
                return result
        except Exception as e:
            logging.error(e)

    @async_log
    async def process_result_task(self, data: T.Dict[str, T.Any]):
        instance, user_id, competence = await self.get_uq_extra_params(
            TgUser.id, Question.competence, uq_id=data['uq_id'])
        request_text = await self.format_user_qa_to_text(instance.user_answer_json)
        result = await self.get_result(request_text, competence)
        if result:
            await self.update_uq(instance, result.model_dump())
            await self.gpt_producer.create_task_return_result_to_user(
                user_id, result, competence, premium_queue=data['priority'])

    @async_log
    async def process_result_local_model_task(self, data: T.Dict[str, T.Any]):
        instance, user_id, competence = await self.get_uq_extra_params(
            TgUser.id, Question.competence, uq_id=data['uq_id'])
        request_text = await UserQuestionService.format_question_answer_to_text(
            instance.user_answer_json['card_text'], instance.user_answer_json['user_answer']
        )
        result = await self.result_service.generate_result(request_text, competence, local_model=True)
        if data['priority']:
            premium_result = await self.result_service.generate_result(request_text, competence)
            vocabulary = premium_result.vocabulary
            result.append(vocabulary)
        if result:
            await self.update_uq(instance, json.dumps(result))
            await self.gpt_producer.create_task_return_simple_result_to_user(user_id, result, data['priority'])

    async def get_uq_extra_params(self, *select_params, uq_id: int):
        async with self.session() as session:
            query = select(TgUserQuestion, *select_params)
            if TgUser.id in select_params:
                query = query.join(TgUser, TgUserQuestion.user_id == TgUser.id)
            if Question.competence in select_params:
                query = query.join(Question, TgUserQuestion.question_id == Question.id)
            query = query.where(and_(TgUserQuestion.id == uq_id))
            result = await session.execute(query)
            instance, user_id, competence = result.first()
            return instance, user_id, competence

    async def update_uq(self, instance: TgUserQuestion, user_result_json):
        async with self.session() as session:
            instance.user_result_json = user_result_json
            instance.status = True
            session.add(instance)

            user_query = await session.execute(select(TgUser).where(and_(TgUser.id == instance.user_id)))
            user = user_query.scalar_one_or_none()
            user.completed_questions += 1
            session.add(user)
            if user.completed_questions == 3 and user.referrer_id:
                referrer_query = await session.execute(
                    select(TgUser).where(and_(TgUser.id == user.referrer_id))
                )
                referrer = referrer_query.scalar_one_or_none()
                if referrer:
                    referrer.pts += 5
                    session.add(referrer)
            await session.commit()

    @staticmethod
    async def format_user_qa_to_text(user_answer_json: T.Dict) -> str:
        parts_text = []
        for part, questions in user_answer_json.items():
            part_num = part.split('_')[1]
            part_text = [f"Part {part_num}:\n"]
            for i, q in enumerate(questions):
                part_text.append(f"Q: {q['card_text']}\nA: {q['user_answer']}\n")
            parts_text.append("".join(part_text))
        return "\n".join(parts_text)
