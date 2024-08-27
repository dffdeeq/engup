import typing as T # noqa

from src.libs.factories.gpt.base import BaseGPTClient
from src.libs.factories.gpt.models.result import TranscriptResult
from src.libs.factories.gpt.routes import GENERATE_TRANSCRIPT


class GenerateTranscriptMixin(BaseGPTClient):
    async def generate_transcript(self, text: str) -> TranscriptResult:
        response = await self.request(
            'POST',
            GENERATE_TRANSCRIPT,
            data={'text': text},
        )
        response = response.body.get('response')
        parsed_response = {
            'text': response.get('text', ''),
            'self_correction_list': response.get('self-correction list', []),
            'repetitions_list': response.get('repetitions list', [])
        }
        return TranscriptResult(**parsed_response)
