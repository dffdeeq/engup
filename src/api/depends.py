from src.libs.adapter import Adapter
from src.postgres.factory import initialize_postgres_pool
from src.postgres.models.metrics_data import MetricsData
from src.rabbitmq.producer.factories.apihost import ApiHostProducer
from src.repos.factories.metrics_data import MetricsDataRepo
from src.settings import Settings

settings = Settings.new()


async def get_apihost_producer() -> ApiHostProducer:
    return ApiHostProducer(
        dsn_string=settings.rabbitmq.dsn,
        adapter=Adapter(settings)
    )


async def get_metrics_repo() -> MetricsDataRepo:
    session = initialize_postgres_pool(settings.postgres)
    return MetricsDataRepo(
        model=MetricsData,
        session=session
    )
