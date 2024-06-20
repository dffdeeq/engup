from src.libs.adapter import Adapter
from src.rabbitmq.producer.factories.apihost import ApiHostProducer
from src.settings import Settings


async def get_apihost_producer() -> ApiHostProducer:
    settings = Settings.new()
    apihost_producer = ApiHostProducer(
        dsn_string=settings.rabbitmq.dsn,
        adapter=Adapter(settings)
    )
    return apihost_producer
