from fastapi import APIRouter, Depends

from src.api.depends import get_apihost_producer
from src.api.schemas import TranscriptionData
from src.rabbitmq.producer.factories.apihost import ApiHostProducer

router = APIRouter()


@router.post("/webhook")
async def webhook(data: TranscriptionData, apihost_producer: ApiHostProducer = Depends(get_apihost_producer)):
    await apihost_producer.create_task_update_answers(data.dump_transcriptions())
