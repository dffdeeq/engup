from src.libs.adapter import Adapter
from src.rabbitmq.producer.factories.apihost import ApiHostProducer
from src.settings import Settings

settings = Settings.new()


async def get_apihost_producer() -> ApiHostProducer:
    return ApiHostProducer(
        dsn_string=settings.rabbitmq.dsn,
        adapter=Adapter(settings)
    )
