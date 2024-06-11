from fastapi import APIRouter

from src.api.schemas import TranscriptionData

router = APIRouter()


@router.post("/webhook")
async def webhook(data: TranscriptionData):
    print(data)
    for transcription in data.transcriptions:
        print(transcription)
