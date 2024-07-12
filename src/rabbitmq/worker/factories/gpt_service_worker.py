import json
import logging
import typing as T  # noqa
from functools import wraps

from aio_pika.abc import AbstractRobustConnection
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.bot.handlers.constants import MessageTemplates, Constants
from src.bot.handlers.utils import generate_section
from src.libs.factories.gpt.models.result import Result
from src.libs.factories.gpt.models.suggestion import Suggestion
from src.postgres.enums import CompetenceEnum
from src.rabbitmq.producer.factories.gpt import GPTProducer
from src.rabbitmq.worker.factory import RabbitMQWorkerFactory
from src.repos.factories.temp_data import TempDataRepo
from src.repos.factories.user_question import TgUserQuestionRepo
from src.services.factories.answer_process import AnswerProcessService
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
        temp_data_repo: TempDataRepo,
        uq_repo: TgUserQuestionRepo,
        connection_pool: AbstractRobustConnection,
        queues_info: T.List[T.Tuple[str, str]],
        result_service: ResultService,
        answer_process_service: AnswerProcessService,
        gpt_producer: GPTProducer,
    ):
        super().__init__(temp_data_repo, connection_pool, queues_info)
        self.temp_data_repo = temp_data_repo
        self.uq_repo = uq_repo
        self.session = session
        self.result_service = result_service
        self.answer_process_service = answer_process_service
        self.gpt_producer = gpt_producer

    @async_log
    async def process_result_local_model_task(self, data: T.Dict[str, T.Any]):
        instance, user, question = await self.uq_repo.get_uq_with_relations(uq_id=data['uq_id'])
        competence = question.competence

        if competence == CompetenceEnum.writing:
            request_text = await UserQuestionService.format_question_answer_to_text(
                instance.user_answer_json['card_text'], instance.user_answer_json['user_answer']
            )
            result = await self.result_service.generate_result(request_text, competence, premium=data['priority'])
            if data['priority']:
                premium_result = await self.result_service.adapter.gpt_client.generate_result(
                    request_text, competence=competence)
                formatted_premium_results = self.format_premium_result(premium_result)
                result.extend(formatted_premium_results)

        elif competence == CompetenceEnum.speaking:
            request_text = await self.format_user_qa_to_answers_only(instance.user_answer_json)
            filepaths = await self.answer_process_service.get_temp_data_filepaths(instance.id)

            additional_request_text = await self.format_user_qa_to_text(instance.user_answer_json)
            additional_result = await self.result_service.adapter.gpt_client.generate_result(
                additional_request_text, competence=competence)
            fluency_coherence = additional_result.competence_results.fluency_coherence

            result = await self.result_service.generate_result(
                request_text, competence, premium=data['priority'],
                voice_filepaths=filepaths, temp_score=fluency_coherence.score)

            section = await generate_section(
                'Fluency and Coherence', fluency_coherence.score, fluency_coherence.enhancements)
            result.append(section)
            general_recommendations = MessageTemplates.GENERAL_RECOMMENDATIONS_TEMPLATE.format(
                vocabulary='\n'.join(f'- {word}' for word in additional_result.vocabulary),
                practice_regularly=Constants.PRACTICE_REGULARLY_DICT[competence]
            )
            result.append(general_recommendations)

        else:
            return

        if result:
            await self.result_service.update_uq(instance, json.dumps(result))
            await self.gpt_producer.create_task_return_simple_result_to_user(user.id, result, data['priority'])

    @staticmethod
    def format_premium_result(result: Result) -> T.List[str]:
        def format_suggestion(suggestion_name: str, suggestion: T.Optional[Suggestion]) -> T.Optional[str]:
            if suggestion is None:
                return None
            formatted_text = f"{suggestion_name}:\n"
            for enhancement in suggestion.enhancements:
                formatted_text += (
                    f"\n{enhancement.basic_suggestion}\n"
                    f"<b>Your answer:</b> {enhancement.source_text}\n"
                    f"<b>Enhanced answer:</b> {enhancement.enhanced_text}\n"
                )
            return formatted_text.strip()

        premium_texts = ['<b>Recommendations</b>', ]
        competence_results = result.competence_results
        suggestion_names = [
            ("Task Achievement", competence_results.task_achievement),
            ("Fluency Coherence", competence_results.fluency_coherence),
            ("Lexical Resources", competence_results.lexical_resources),
            ("Grammatical Range", competence_results.grammatical_range)
        ]
        formatted_suggestions = [format_suggestion(name, suggestion) for name, suggestion in suggestion_names if
                                 suggestion is not None]

        premium_texts.extend(formatted_suggestions)
        vocabulary = '<b>Vocabulary:</b>\n' + '\n'.join(f'- {word}' for word in result.vocabulary)
        premium_texts.append(vocabulary)
        return premium_texts

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

    @staticmethod
    async def format_user_qa_to_answers_only(user_answer_json: T.Dict) -> str:
        return ' '.join(q['user_answer'] for questions in user_answer_json.values() for q in questions)
