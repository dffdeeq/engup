import uuid

from src.libs.factories.mp3tts.base import BaseMP3TTSClient
from src.libs.factories.mp3tts.models.transcription_response import TranscriptionResponse
from src.libs.factories.mp3tts.routes import CONFIRM_TRANSCRIPTION


class ConfirmTranscriptionMixin(BaseMP3TTSClient):
    async def confirm_transcription(self, transcription_id: uuid.UUID) -> TranscriptionResponse:
        payload = {
            "upload_id": str(transcription_id),
            "model": "falcon-en-v3",
            "language": "en",
            "prompt": "Please transcribe this audio.",
            "response_format": "json",
            "temperature": 0.5,
            "webhook": self.settings.webhook_url,
            "timestamp_granularities": [
                "segments",
                "words"
            ]
        }  # **** temp realization **** -> move payload to models or defaults
        response = await self.request('POST', CONFIRM_TRANSCRIPTION, json=payload)
        return TranscriptionResponse(**response.body)
