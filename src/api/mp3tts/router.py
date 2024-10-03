from fastapi import APIRouter, Depends

from src.api.depends import get_apihost_producer
from src.api.mp3tts.schemas import TranscriptionData
from src.rabbitmq.producer.factories.mp3tts import MP3TTSProducer

router = APIRouter()


@router.post("/webhook")
async def webhook(data: TranscriptionData, apihost_producer: MP3TTSProducer = Depends(get_apihost_producer)):
    await apihost_producer.create_task_update_answers(data.dump_transcriptions())
