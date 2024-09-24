from fastapi import APIRouter, Depends

from src.api.depends import get_apihost_producer, get_metrics_repo
from src.api.schemas import TranscriptionData, MetricsData
from src.rabbitmq.producer.factories.mp3tts import MP3TTSProducer
from src.repos.factories.metrics_data import MetricsDataRepo

router = APIRouter()


@router.post("/webhook")
async def webhook(data: TranscriptionData, apihost_producer: MP3TTSProducer = Depends(get_apihost_producer)):
    await apihost_producer.create_task_update_answers(data.dump_transcriptions())


@router.post("/save_metrics")
async def save_metrics(data: MetricsData, metrics_repo: MetricsDataRepo = Depends(get_metrics_repo)):
    await metrics_repo.create_metrics_data(data.uuid, data.metrics_string)
