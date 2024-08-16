import asyncio
import logging

from src.libs.adapter import Adapter
from src.neural_network import ScoreGeneratorNNModel
from src.postgres.factory import initialize_postgres_pool
from src.postgres.models.question import Question
from src.postgres.models.temp_data import TempData
from src.postgres.models.tg_user import TgUser
from src.postgres.models.tg_user_activity import TgUserActivity
from src.postgres.models.tg_user_question import TgUserQuestion, TgUserQuestionMetric
from src.rabbitmq.worker.factories.gpt_service_worker import GPTWorker
from src.rabbitmq.worker.factories.simple_worker import SimpleWorker
from src.repos.factories.activity import ActivityRepo
from src.repos.factories.question import QuestionRepo
from src.repos.factories.temp_data import TempDataRepo
from src.repos.factories.user import TgUserRepo
from src.repos.factories.user_question import TgUserQuestionRepo
from src.repos.factories.user_question_metric import TgUserQuestionMetricRepo
from src.services.factories.answer_process import AnswerProcessService
from src.services.factories.result import ResultService
from src.services.factories.status_service import StatusService
from src.services.factories.tg_user import TgUserService
from src.settings import Settings

for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logging.getLogger('aio_pika').setLevel(logging.WARNING)
logging.getLogger('sqlalchemy').setLevel(logging.WARNING)
logging.getLogger('torch').setLevel(logging.WARNING)
logging.getLogger('pyannote').setLevel(logging.WARNING)
logging.getLogger('pytorch_lightning').setLevel(logging.WARNING)


async def main():
    settings = Settings.new()
    session = initialize_postgres_pool(settings.postgres)
    adapter = Adapter(settings)
    repo = TempDataRepo(TempData, session)
    uq_repo = TgUserQuestionRepo(TgUserQuestion, session)
    user_service = TgUserService(
        TgUserRepo(TgUser, session),
        ActivityRepo(TgUserActivity, session),
        adapter,
        session,
        settings
    )

    result_service = ResultService(
        repo=QuestionRepo(Question, session),
        adapter=adapter,
        session=session,
        settings=settings,
        nn_service=ScoreGeneratorNNModel(settings.nn_models, TgUserQuestionMetricRepo(TgUserQuestionMetric, session)),
        user_service=user_service,
        simple_worker=SimpleWorker(
            repo=repo,
            dsn_string=settings.rabbitmq.dsn,
            queue_name='public'
        )
    )
    answer_process_service = AnswerProcessService(
        repo=repo,
        adapter=adapter,
        session=session,
        settings=settings,
        user_qa_repo=uq_repo
    )
    status_service = StatusService(
        TgUserQuestionRepo(TgUserQuestion, session),
        adapter=adapter,
        session=session,
        settings=settings,
    )
    gpt_worker = GPTWorker(
        temp_data_repo=repo,
        uq_repo=uq_repo,
        session=session,
        result_service=result_service,
        dsn_string=settings.rabbitmq.dsn,
        queue_name='gpt',
        heartbeat=600,
        answer_process_service=answer_process_service,
        status_service=status_service,
        user_service=user_service
    )
    await gpt_worker.start_listening(
        'gpt_generate_result_use_local_model', gpt_worker.process_result_local_model_task)


if __name__ == '__main__':
    asyncio.run(main())
