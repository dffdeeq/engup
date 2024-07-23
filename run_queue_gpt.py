import asyncio
import logging
import time

from src.libs.adapter import Adapter
from src.neural_network import ScoreGeneratorNNModel
from src.postgres.factory import initialize_postgres_pool
from src.postgres.models.question import Question
from src.postgres.models.temp_data import TempData
from src.postgres.models.tg_user_question import TgUserQuestion
from src.rabbitmq.worker.factories.gpt_service_worker import GPTWorker
from src.repos.factories.question import QuestionRepo
from src.repos.factories.temp_data import TempDataRepo
from src.repos.factories.user_question import TgUserQuestionRepo
from src.services.factories.answer_process import AnswerProcessService
from src.services.factories.result import ResultService
from src.services.factories.status_service import StatusService
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
    start_time = time.time()
    logger.info("Starting the main function")

    settings = Settings.new()
    session = initialize_postgres_pool(settings.postgres)
    adapter = Adapter(settings)
    logger.info(f"Adapter initialized: {time.time() - start_time:.2f} seconds elapsed")
    repo = TempDataRepo(TempData, session)
    uq_repo = TgUserQuestionRepo(TgUserQuestion, session)

    result_service = ResultService(
        repo=QuestionRepo(Question, session),
        adapter=adapter,
        session=session,
        settings=settings,
        nn_service=ScoreGeneratorNNModel(settings.nn_models)
    )
    logger.info(f"ResultService initialized: {time.time() - start_time:.2f} seconds elapsed")

    answer_process_service = AnswerProcessService(
        repo=repo,
        adapter=adapter,
        session=session,
        settings=settings,
        user_qa_repo=uq_repo
    )
    logger.info(f"AnswerProcessService initialized: {time.time() - start_time:.2f} seconds elapsed")

    status_service = StatusService(
        uq_repo,
        adapter,
        session,
        settings
    )

    gpt_worker = GPTWorker(
        temp_data_repo=repo,
        uq_repo=uq_repo,
        session=session,
        result_service=result_service,
        dsn_string=settings.rabbitmq.dsn,
        queue_name='gpt',
        answer_process_service=answer_process_service,
        status_service=status_service,
    )
    logger.info(f"GPTWorker initialized: {time.time() - start_time:.2f} seconds elapsed")
    await gpt_worker.start_listening(
        'gpt_generate_result_use_local_model', gpt_worker.process_result_local_model_task)
    logger.info(f"Started listening: {time.time() - start_time:.2f} seconds elapsed")


if __name__ == '__main__':
    asyncio.run(main())
